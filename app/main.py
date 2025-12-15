from fastapi import FastAPI, Depends, HTTPException, Security, BackgroundTasks, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
from .database import get_db
from . import models, schemas, database, crud, services
from .security import verify_token
import time as sys_time
from sqlalchemy.exc import OperationalError

# Retry connecting to the database
max_retries = 10
retry_interval = 2

for i in range(max_retries):
    try:
        models.Base.metadata.create_all(bind=database.engine)
        break
    except OperationalError as e:
        if i == max_retries - 1:
            raise e
        print(f"Database not ready, retrying in {retry_interval} seconds...")
        sys_time.sleep(retry_interval)


app = FastAPI(dependencies=[Depends(verify_token)])


@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(
    appointment: schemas.AppointmentCreate, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    token: str = Depends(verify_token)
):
    print(f"DEBUG: Received appointment creation request: {appointment}")
    
    # Check for existing appointment
    existing_appt = crud.get_appointment_by_doctor_and_time(
        db, appointment.doctor_name, appointment.start_time
    )
    if existing_appt:
        print(f"DEBUG: Appointment already exists at {appointment.start_time}")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This time slot is already booked."
        )

    # Extract trigger flag before CRUD
    trigger_robot = appointment.trigger_robot
    print(f"DEBUG: trigger_robot flag = {trigger_robot}")
    
    # Create in DB
    db_appointment = crud.create_appointment(db, appointment)
    print(f"DEBUG: Appointment created in DB with ID: {db_appointment.id}")

    # Trigger Robot if requested
    if trigger_robot:
        print(f"DEBUG: Preparing to trigger robot...")
        # Prepare payload
        robot_payload = appointment.model_dump()
        del robot_payload["trigger_robot"]
        
        # Serialize datetimes
        if isinstance(robot_payload.get("start_time"), datetime):
            robot_payload["start_time"] = robot_payload["start_time"].isoformat()
        if isinstance(robot_payload.get("end_time"), datetime):
            robot_payload["end_time"] = robot_payload["end_time"].isoformat()
        
        print(f"DEBUG: Adding robot task to background with payload: {robot_payload}")
        background_tasks.add_task(services.execute_robot_task, robot_payload, token)
        print(f"DEBUG: Robot task added to background tasks")
    else:
        print(f"DEBUG: Robot trigger NOT requested (trigger_robot={trigger_robot})")

    return db_appointment

@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = crud.get_appointments(db, skip=skip, limit=limit)
    return appointments


@app.get("/appointments/available_slots/")
def get_available_slots(agenda: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Returns available slots for the next 7 days.
    If 'agenda' is provided, filters by that agenda.
    If not, returns slots grouped by each agenda name.
    """
    today = datetime.now().date()
    end_date = today + timedelta(days=7)

    if agenda:
        # Single agenda mode - return slots for specific agenda
        appointments = crud.get_appointments_for_range(db, agenda, today, end_date)
        
        # Organize appointments by date
        appointments_by_date = {}
        for appt in appointments:
            appt_date = appt.start_time.date()
            if appt_date not in appointments_by_date:
                appointments_by_date[appt_date] = []
            appointments_by_date[appt_date].append(appt)

        result = {
            "agenda": agenda,
            "days": []
        }

        # Iterate through each day to calculate availability
        current_date = today
        while current_date <= end_date:
            # Skip weekends and holidays
            if not services.is_working_day(current_date):
                current_date += timedelta(days=1)
                continue
                
            day_str = current_date.strftime("%Y-%m-%d")
            day_appointments = appointments_by_date.get(current_date, [])
            
            # Calculate available slots for this specific day
            available_slots = services.calculate_available_slots(current_date, day_appointments)
            
            result["days"].append({
                "date": day_str,
                "available_slots": available_slots
            })
            
            current_date += timedelta(days=1)

        return result
    
    else:
        # Multi-agenda mode - return slots grouped by each agenda
        all_appointments = crud.get_appointments_for_range(db, None, today, end_date)
        
        # Group appointments by agenda
        appointments_by_agenda = {}
        for appt in all_appointments:
            agenda_name = appt.agenda if appt.agenda else "Unknown"
            if agenda_name not in appointments_by_agenda:
                appointments_by_agenda[agenda_name] = []
            appointments_by_agenda[agenda_name].append(appt)
        
        # Calculate slots for each agenda
        agendas_result = []
        
        for agenda_name, agenda_appointments in appointments_by_agenda.items():
            # Organize by date
            appointments_by_date = {}
            for appt in agenda_appointments:
                appt_date = appt.start_time.date()
                if appt_date not in appointments_by_date:
                    appointments_by_date[appt_date] = []
                appointments_by_date[appt_date].append(appt)
            
            days = []
            current_date = today
            while current_date <= end_date:
                # Skip weekends and holidays
                if not services.is_working_day(current_date):
                    current_date += timedelta(days=1)
                    continue
                    
                day_str = current_date.strftime("%Y-%m-%d")
                day_appointments = appointments_by_date.get(current_date, [])
                
                # Calculate available slots for this specific day
                available_slots = services.calculate_available_slots(current_date, day_appointments)
                
                days.append({
                    "date": day_str,
                    "available_slots": available_slots
                })
                
                current_date += timedelta(days=1)
            
            agendas_result.append({
                "agenda": agenda_name,
                "days": days
            })
        
        return {"agendas": agendas_result}

@app.get("/appointments/{appointment_id}", response_model=schemas.Appointment)
def read_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = crud.get_appointment(db, appointment_id=appointment_id)
    if db_appointment is None:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return db_appointment

@app.post("/appointments/sync/")
def sync_appointments(appointments: List[schemas.AppointmentCreate], db: Session = Depends(get_db)):
    if not appointments:
        return {"status": "skipped", "message": "Empty list provided"}
    
    return crud.sync_appointments(db, appointments)


