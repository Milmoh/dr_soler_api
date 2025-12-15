import os
import requests
from datetime import datetime, time, timedelta

def execute_robot_task(appointment_data: dict, token: str):
    """
    Triggers the 'agendar_cita' robot on the Host Agent.
    """
    host_agent_url = os.getenv("HOST_AGENT_URL", "http://host.docker.internal:8001")
    url = f"{host_agent_url}/run-robot/agendar_cita"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Payload expected by the robot
    payload = {
        "payload": appointment_data
    }
    
    try:
        print(f"Triggering robot at {url} with data: {appointment_data}")
        # We use a long timeout just in case, but since this is bg task, it's fine.
        response = requests.post(url, json=payload, headers=headers, timeout=600)
        print(f"Robot trigger response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to trigger robot: {e}")

def calculate_available_slots(date_obj, existing_appointments):
    """
    Calculates available 15-minute slots for a specific date given existing appointments.
    Working hours: 09:00-14:00, 16:00-20:00.
    """
    # Define working hours
    morning_start = time(9, 0)
    morning_end = time(14, 0)
    afternoon_start = time(16, 0)
    afternoon_end = time(20, 0)
    slot_duration = timedelta(minutes=15)

    possible_slots = []

    # Generate Morning Slots
    current = datetime.combine(date_obj, morning_start)
    end = datetime.combine(date_obj, morning_end)
    while current < end:
        possible_slots.append(current)
        current += slot_duration

    # Generate Afternoon Slots
    current = datetime.combine(date_obj, afternoon_start)
    end = datetime.combine(date_obj, afternoon_end)
    while current < end:
        possible_slots.append(current)
        current += slot_duration

    # Create a set of occupied start times
    busy_times = {appt.start_time for appt in existing_appointments}

    available = [slot for slot in possible_slots if slot not in busy_times]
    
    return available
