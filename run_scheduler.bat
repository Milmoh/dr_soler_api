@echo off
echo Starting Scheduler Service...

if not exist "venv" (
    echo Virtual environment not found. Please run 'setup_env.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate

REM Set environment variables
set HOST_AGENT_URL=http://localhost:8001

echo Running Scheduler...
python -u -m app.scheduler_service

pause