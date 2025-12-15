import asyncio
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel
import uvicorn
from fastapi import FastAPI, HTTPException, Security, status, Depends
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials # Moved to app.security
import subprocess
import os
import sys
import logging

try:
    from app.security import verify_token
except ImportError:
    # Handle case where 'app' is not in python path directly (though it should be if run from root)
    # We can append current dir to path or assume user runs correctly
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from app.security import verify_token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("host_agent")

# Configuration
ROBOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robots")
ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")

# Pre-load ENV to os.environ for app.security to work
if os.path.exists(ENV_FILE):
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            # Only set if not already set (allow system env overrides)
            if key not in os.environ:
                 os.environ[key] = value

app = FastAPI(dependencies=[Depends(verify_token)])

# Global lock for serial execution
robot_lock = asyncio.Lock()

class RobotRequest(BaseModel):
    payload: Optional[Dict[str, Any]] = None

def get_robot_env():
    """
    Creates an environment dict for the robot.
    Reads .env, merges with os.environ, and patches DATABASE_URL for Host usage.
    """
    env = os.environ.copy()
    
    # Simple .env parser to avoid extra dependencies
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                env[key] = value

    # PATCH: If DATABASE_URL points to 'db' (docker service), redirect to localhost:5433
    # This allows the same .env to work for both Docker (internal) and Host (external)
    if "DATABASE_URL" in env and "@db" in env["DATABASE_URL"]:
        # Replace hostname 'db' with 'localhost' and ensure port is 5433
        # Assuming format postgresql://user:pass@db/dbname or @db:5432/dbname
        new_url = env["DATABASE_URL"].replace("@db", "@localhost")
        
        # If port is missing or 5432, switch to 5433 (the exposed port)
        if ":5432" in new_url:
            new_url = new_url.replace(":5432", ":5433")
        elif "@localhost/" in new_url:
            new_url = new_url.replace("@localhost/", "@localhost:5433/")
            
        env["DATABASE_URL"] = new_url
        logger.info(f"Patched DATABASE_URL for host execution: {new_url}")
        
    return env

@app.post("/run-robot/{robot_name}")
async def run_robot(robot_name: str, request: RobotRequest = None):
    """
    Executes a robot script/executable.
    Ensures only one robot runs at a time using a global lock.
    """
    logger.info(f"Received request to run robot: {robot_name}")
    
    # Determine the script path
    potential_paths = [
        os.path.join(ROBOTS_DIR, robot_name, f"{robot_name}.exe"),
        os.path.join(ROBOTS_DIR, f"{robot_name}.exe"),
        os.path.join(ROBOTS_DIR, robot_name, "main.py"),
        os.path.join(ROBOTS_DIR, f"{robot_name}.py"),
        os.path.join(ROBOTS_DIR, robot_name, "rdp_bot.py"),
    ]
    
    script_path = None
    for path in potential_paths:
        if os.path.exists(path):
            script_path = path
            break
            
    if not script_path:
        raise HTTPException(status_code=404, detail=f"Robot '{robot_name}' not found")

    # Acquire lock to ensure serial execution
    if robot_lock.locked():
        logger.info(f"Robot execution locked. Waiting for other robots to finish...")

    async with robot_lock:
        try:
            logger.info(f"Acquired lock. Preparing to execute: {script_path}")
            
            cmd = []
            if script_path.endswith(".exe"):
                cmd = [script_path]
            else:
                cmd = [sys.executable, script_path]

            # Pass payload as JSON string argument if provided
            if request and request.payload:
                cmd.append(json.dumps(request.payload))

            logger.info(f"Executing command: {cmd}")
            
            # Use asyncio subprocess to invoke and wait
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=get_robot_env()
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"Robot failed with code {process.returncode}")
                logger.error(f"Stderr: {stderr.decode()}")
                raise Exception(f"Robot failed: {stderr.decode()}")

            logger.info(f"Robot finished successfully")
            return {
                "status": "completed", 
                "robot": robot_name, 
                "path": script_path, 
                "output": stdout.decode()
            }
            
        except Exception as e:
            logger.error(f"Failed to execute robot: {e}")
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting Host Agent on port 8001...")
    print("Ensure you have installed dependencies: pip install fastapi uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8001)
