@echo off
echo Starting Web API (FastAPI)...

if not exist "venv" (
    echo Virtual environment not found. Please run 'setup_env.bat' first.
    pause
    exit /b 1
)

call venv\Scripts\activate

REM Force UTF-8 for Postgres messages to avoid UnicodeDecodeError on Windows
set PGCLIENTENCODING=utf8
set PYTHONUTF8=1

REM Override DATABASE_URL for local execution (localhost instead of db)
set DATABASE_URL=postgresql://admin:password@localhost/dr_soler_db

REM Using uvicorn as defined in Dockerfile CMD
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

pause
