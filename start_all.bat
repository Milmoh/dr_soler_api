@echo off
echo Starting All Services...

start "Host Agent" cmd /k "run_host_agent.bat"
start "Web API" cmd /k "run_web.bat"
start "Scheduler" cmd /k "run_scheduler.bat"

echo.
echo Services started in new windows.
echo Web API running on http://localhost:8000
echo Host Agent running on http://localhost:8001
echo Scheduler running in background.
