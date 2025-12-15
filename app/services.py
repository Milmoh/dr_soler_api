import os
import requests
from datetime import datetime, time, timedelta, date

def is_working_day(date_obj):
    """
    Check if a date is a working day (not weekend or Spanish holiday in Comunidad Valenciana).
    Returns True if it's a working day, False otherwise.
    """
    # Check if weekend (Saturday=5, Sunday=6)
    if date_obj.weekday() >= 5:
        return False
    
    # Spanish National Holidays (fixed dates)
    year = date_obj.year
    national_holidays = [
        date(year, 1, 1),   # Año Nuevo
        date(year, 1, 6),   # Reyes Magos
        date(year, 5, 1),   # Día del Trabajo
        date(year, 8, 15),  # Asunción de la Virgen
        date(year, 10, 12), # Fiesta Nacional de España
        date(year, 11, 1),  # Todos los Santos
        date(year, 12, 6),  # Día de la Constitución
        date(year, 12, 8),  # Inmaculada Concepción
        date(year, 12, 25), # Navidad
    ]
    
    # Comunidad Valenciana specific holidays
    cv_holidays = [
        date(year, 3, 19),  # San José (Fallas)
        date(year, 10, 9),  # Día de la Comunidad Valenciana
    ]
    
    # Easter-based holidays (approximate - these change each year)
    # For 2025-2026, adding common dates
    easter_holidays_2025 = [
        date(2025, 4, 17),  # Jueves Santo
        date(2025, 4, 18),  # Viernes Santo
        date(2025, 4, 21),  # Lunes de Pascua
    ]
    
    easter_holidays_2026 = [
        date(2026, 4, 2),   # Jueves Santo
        date(2026, 4, 3),   # Viernes Santo
        date(2026, 4, 6),   # Lunes de Pascua
    ]
    
    all_holidays = national_holidays + cv_holidays
    if year == 2025:
        all_holidays.extend(easter_holidays_2025)
    elif year == 2026:
        all_holidays.extend(easter_holidays_2026)
    
    return date_obj not in all_holidays

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
