# Local Setup Guide (No Docker)

Since you are running on Windows without Docker, follow these steps to set up your environment.

## 1. Prerequisites

### PostgreSQL
You need a local PostgreSQL database running.
1.  **Download & Install**: [PostgreSQL for Windows](https://www.postgresql.org/download/windows/)
2.  **During Installation**:
    *   Set a password for the `postgres` user (remember this!).
    *   Keep the default port `5432` (unless you have a reason to change it).
3.  **Create Database**:
    *   Open **pgAdmin** (installed with Postgres) or use the command line `psql`.
    *   Create a new database named `dr_soler` (or match what is in your `.env`).

### Python
Ensure Python 3.9+ is installed and identifying as `python` in your terminal.

## 2. Configuration (.env)

You likely already have a `.env` file. You need to modify the `DATABASE_URL` to point to your local machine instead of the Docker container.

**Open `.env` and update:**

```ini
# CHANGE THIS
# Old (Docker): DATABASE_URL=postgresql://user:pass@db:5432/dbname
# New (Local):  DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/dr_soler

# ENSURE THESE ARE SET
API_BEARER_TOKEN=some_secure_token
INTERVAL_SECONDS=60
ROBOT_NAME=listar_citas
```

*Note: Replace `YOUR_PASSWORD` with the password you set during Postgres installation.*

## 3. Installation

Run the setup script to create a virtual environment and install dependencies:

```cmd
setup_env.bat
```

## 4. Running the App

You can start all services (Web API + Host Agent + Scheduler) at once:

```cmd
start_all.bat
```

Or run them individually:
*   **Web API**: `run_web.bat`
*   **Host Agent**: `run_host_agent.bat`
*   **Scheduler**: `run_scheduler.bat`

## 5. Access

*   **API Docs**: http://localhost:8000/docs
*   **Host Agent**: http://localhost:8001/docs
