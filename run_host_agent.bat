@echo off
echo Starting Host Agent...

if not exist "venv" (
    echo Virtual environment not found. Please run 'setup_env.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate

REM Host Agent runs on port 8001
echo Running Host Agent on port 8001...
python host_agent.py

pause
