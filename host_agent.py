import uvicorn
from fastapi import FastAPI, HTTPException
import subprocess
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("host_agent")

app = FastAPI()

# Configuration
ROBOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robots")

@app.post("/run-robot/{robot_name}")
async def run_robot(robot_name: str):
    """
    Executes a robot script located in the robots directory.
    """
    logger.info(f"Received request to run robot: {robot_name}")
    
    # Determine the script path
    # Support both flat files and directories with main scripts
    potential_paths = [
        os.path.join(ROBOTS_DIR, f"{robot_name}.py"),
        os.path.join(ROBOTS_DIR, robot_name, "rdp_bot.py"), # Specific for rdp_bot
        os.path.join(ROBOTS_DIR, robot_name, "main.py")
    ]
    
    script_path = None
    for path in potential_paths:
        if os.path.exists(path):
            script_path = path
            break
            
    if not script_path:
        raise HTTPException(status_code=404, detail=f"Robot '{robot_name}' not found")
        
    try:
        # Execute the script using the current python interpreter
        # This ensures we use the host's python environment
        logger.info(f"Executing: {script_path}")
        subprocess.Popen([sys.executable, script_path])
        return {"status": "started", "robot": robot_name, "path": script_path}
        
    except Exception as e:
        logger.error(f"Failed to start robot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print("Starting Host Agent on port 8001...")
    print("Ensure you have installed dependencies: pip install fastapi uvicorn")
    uvicorn.run(app, host="0.0.0.0", port=8001)
