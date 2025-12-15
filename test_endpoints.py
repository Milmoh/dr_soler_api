import requests
import time
import os

BASE_URL = "http://localhost:8000"
TOKEN = os.getenv("API_BEARER_TOKEN") # Match your .env default or actual value

HEADERS = {
    "Authorization": f"Bearer {TOKEN}"
}

def wait_for_api():
    for _ in range(30):
        try:
            # Docs page might be public, but let's check a secured endpoint lightly or just connection
            response = requests.get(f"{BASE_URL}/docs")
            if response.status_code == 200:
                print("API is up!")
                return
        except requests.exceptions.ConnectionError:
            pass
        print("Waiting for API...")
        time.sleep(1)
    raise Exception("API failed to start")

def test_endpoints():
    # Create an appointment
    print("Creating appointment...")
    new_appointment = {
        "doctor_name": "Dr. Soler",
        "patient_name": "John Doe",
        "start_time": "2025-12-25T10:00:00",
        "agenda": "General Checkup"
    }
    response = requests.post(f"{BASE_URL}/appointments/", json=new_appointment, headers=HEADERS)
    if response.status_code != 200:
        print(f"Failed to create: {response.status_code} - {response.text}")
    assert response.status_code == 200
    created_appt = response.json()
    print(f"Created: {created_appt}")

    # List all appointments
    print("Listing all appointments...")
    response = requests.get(f"{BASE_URL}/appointments/", headers=HEADERS)
    assert response.status_code == 200
    all_appts = response.json()
    print(f"All appointments: {len(all_appts)}")
    assert len(all_appts) >= 1

    # Get specific appointment
    print("Getting specific appointment...")
    appt_id = created_appt['id']
    response = requests.get(f"{BASE_URL}/appointments/{appt_id}", headers=HEADERS)
    assert response.status_code == 200
    fetched_appt = response.json()
    assert fetched_appt['id'] == appt_id
    print(f"Fetched: {fetched_appt}")

    print("All tests passed!")

if __name__ == "__main__":
    wait_for_api()
    test_endpoints()
