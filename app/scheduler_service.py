import time
import requests
import logging
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scheduler_service")

# Configuration
QRES_PATH=r"C:\qres\QRes.exe"
HOST_AGENT_URL = os.getenv("HOST_AGENT_URL", "http://host.docker.internal:8001")
ROBOT_NAME = os.getenv("ROBOT_NAME", "robot_listar_citas")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 300)) # 5 minutes default
API_BEARER_TOKEN = os.getenv("API_BEARER_TOKEN")

def force_resolution():
    """Intenta forzar la resolución usando la ruta absoluta"""
    try:
        # Verificamos si existe en esa ruta específica
        if os.path.exists(QRES_PATH):
            logger.info(f"Ejecutando QRes desde: {QRES_PATH}")
            # Ejecutamos usando la ruta completa
            subprocess.run([QRES_PATH, "/x:1280", "/y:800"], check=False, stdout=subprocess.DEVNULL)
        else:
            logger.error(f"ERROR CRÍTICO: No encuentro QRes.exe en: {QRES_PATH}")
            logger.error("Por favor revisa la ruta en el script.")
    except Exception as e:
        logger.error(f"Error al intentar cambiar resolución: {e}")

def trigger_robot():
    force_resolution()
    url = f"{HOST_AGENT_URL}/run-robot/{ROBOT_NAME}"
    logger.info(f"Triggering robot at {url}")
    
    headers = {}
    if API_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {API_BEARER_TOKEN}"
    else:
        logger.warning("API_BEARER_TOKEN not set. Request might fail if host agent is secured.")

    try:
        # Timeout increased to 10 minutes (600s) to wait for robot completion
        response = requests.post(url, timeout=600, headers=headers)
        if response.status_code == 200:
            logger.info(f"Successfully triggered robot: {response.json()}")
        else:
            logger.error(f"Failed to trigger robot. Status: {response.status_code}, Response: {response.text}")
    except requests.exceptions.ConnectionError:
        logger.error(f"Could not connect to Host Agent at {HOST_AGENT_URL}. Is it running on the host?")
    except Exception as e:
        logger.error(f"Error triggering robot: {e}")

def main():
    logger.info(f"Starting Scheduler Service")
    logger.info(f"Target: {HOST_AGENT_URL}")
    logger.info(f"Robot: {ROBOT_NAME}")
    logger.info(f"Interval: {INTERVAL_SECONDS} seconds")
    
    # Initial run
    trigger_robot()
    
    while True:
        logger.info(f"Sleeping for {INTERVAL_SECONDS} seconds...")
        time.sleep(INTERVAL_SECONDS)
        trigger_robot()

if __name__ == "__main__":
    main()
