@echo off
setlocal
echo Setting up Python Virtual Environment...

REM Check for Python
set PYTHON_CMD=python

%PYTHON_CMD% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 'python' command not found. Checking for 'py' launcher...
    set PYTHON_CMD=py
    py --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo Python is not installed or not in PATH. Please install Python 3.9+.
        pause
        exit /b 1
    )
)

echo Using Python command: %PYTHON_CMD%

REM Create venv if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment 'venv'...
    %PYTHON_CMD% -m venv venv
) else (
    echo Virtual environment 'venv' already exists.
)

REM Activate and install requirements
echo activating venv...
call venv\Scripts\activate

echo Installing dependencies from requirements.txt...
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup Complete!
echo You can now run 'start_all.bat' to start the services.
pause
