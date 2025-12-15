@echo off
echo Starting Dr Soler API System...

REM 1. Start Docker Containers
echo Starting Database and API containers...
docker compose up -d --build
IF %ERRORLEVEL% NEQ 0 (
    echo Docker compose failed to start!
    pause
    exit /b %ERRORLEVEL%
)

REM 2. Wait a moment for DB to be potentially ready
timeout /t 5 /nobreak

REM 3. Start Host Agent in a new window using proper Python command
echo Starting Host Agent...
start "Host Agent" cmd /k "python host_agent.py"

echo System started successfully.
echo API available at http://localhost:8000
echo Host Agent available at http://localhost:8001
