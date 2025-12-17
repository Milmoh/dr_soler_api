@echo off
echo Starting Scheduler Service...

if not exist "venv" (
    echo Virtual environment not found. Please run 'setup_env.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate

REM Set environment variables specific to local execution if not in .env
REM These mirror the docker-compose environment for scheduler
set HOST_AGENT_URL=http://localhost:8001
REM ROBOT_NAME is likely in .env, but can be set here if needed

echo Running Scheduler...
python -u -m app.scheduler_service

pause
