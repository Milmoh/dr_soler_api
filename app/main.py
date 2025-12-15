from fastapi import FastAPI, Depends, HTTPException, Security, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
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
    # Check for existing appointment
    existing_appt = crud.get_appointment_by_doctor_and_time(
        db, appointment.doctor_name, appointment.start_time
    )
    if existing_appt:
        return existing_appt

    # Extract trigger flag before CRUD
    trigger_robot = appointment.trigger_robot
    
    # Create in DB
    db_appointment = crud.create_appointment(db, appointment)

    # Trigger Robot if requested
    if trigger_robot:
        # Prepare payload
        robot_payload = appointment.model_dump()
        del robot_payload["trigger_robot"]
        
        # Serialize datetimes
        if isinstance(robot_payload.get("start_time"), datetime):
            robot_payload["start_time"] = robot_payload["start_time"].isoformat()
        if isinstance(robot_payload.get("end_time"), datetime):
            robot_payload["end_time"] = robot_payload["end_time"].isoformat()
            
        background_tasks.add_task(services.execute_robot_task, robot_payload, token)

    return db_appointment

@app.get("/appointments/", response_model=List[schemas.Appointment])
def read_appointments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    appointments = crud.get_appointments(db, skip=skip, limit=limit)
    return appointments

@app.get("/appointments/available-slots/")
def get_available_slots(doctor_name: str, date: str, db: Session = Depends(get_db)):
    try:
        query_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Get existing appointments for that day
    appointments = crud.get_appointments_for_day(db, doctor_name, query_date)

    # Calculate available slots
    available = services.calculate_available_slots(query_date, appointments)

    return {
        "doctor": doctor_name, 
        "date": date, 
        "available_slots": available
    }

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


