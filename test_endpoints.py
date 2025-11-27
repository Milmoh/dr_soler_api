import requests
import time

BASE_URL = "http://localhost:8000"

def wait_for_api():
    for _ in range(30):
        try:
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
        "patient_name": "John Doe",
        "date": "2023-10-27T10:00:00",
        "description": "General Checkup",
        "is_available": False
    }
    response = requests.post(f"{BASE_URL}/appointments/", json=new_appointment)
    assert response.status_code == 200
    created_appt = response.json()
    print(f"Created: {created_appt}")

    # Create an available appointment
    print("Creating available appointment...")
    avail_appointment = {
        "patient_name": "Jane Smith",
        "date": "2023-10-28T11:00:00",
        "description": "Dental Cleaning",
        "is_available": True
    }
    response = requests.post(f"{BASE_URL}/appointments/", json=avail_appointment)
    assert response.status_code == 200
    print(f"Created available: {response.json()}")

    # List all appointments
    print("Listing all appointments...")
    response = requests.get(f"{BASE_URL}/appointments/")
    assert response.status_code == 200
    all_appts = response.json()
    print(f"All appointments: {len(all_appts)}")
    assert len(all_appts) >= 2

    # List available appointments
    print("Listing available appointments...")
    response = requests.get(f"{BASE_URL}/appointments/available/")
    assert response.status_code == 200
    avail_appts = response.json()
    print(f"Available appointments: {len(avail_appts)}")
    # Should be at least 1 (the one we just created)
    assert len(avail_appts) >= 1
    for appt in avail_appts:
        assert appt['is_available'] == True

    # Get specific appointment
    print("Getting specific appointment...")
    appt_id = created_appt['id']
    response = requests.get(f"{BASE_URL}/appointments/{appt_id}")
    assert response.status_code == 200
    fetched_appt = response.json()
    assert fetched_appt['id'] == appt_id
    print(f"Fetched: {fetched_appt}")

    print("All tests passed!")

if __name__ == "__main__":
    wait_for_api()
    test_endpoints()
