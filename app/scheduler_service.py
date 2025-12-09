import time
import requests
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("scheduler_service")

# Configuration
HOST_AGENT_URL = os.getenv("HOST_AGENT_URL", "http://host.docker.internal:8001")
ROBOT_NAME = os.getenv("ROBOT_NAME", "robot_listar_citas")
INTERVAL_SECONDS = int(os.getenv("INTERVAL_SECONDS", 300)) # 5 minutes default

def trigger_robot():
    url = f"{HOST_AGENT_URL}/run-robot/{ROBOT_NAME}"
    logger.info(f"Triggering robot at {url}")
    
    try:
        response = requests.post(url, timeout=5)
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
