from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime, timedelta, time
from typing import List, Optional

def get_appointment_by_doctor_and_time(db: Session, doctor_name: str, start_time: datetime):
    return db.query(models.Appointment).filter(
        models.Appointment.doctor_name == doctor_name,
        models.Appointment.start_time == start_time
    ).first()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    appt_data = appointment.model_dump()
    # Remove trigger_robot if present (though schema should have handled it in main, safe to check)
    if "trigger_robot" in appt_data:
        del appt_data["trigger_robot"]

    # Default end_time logic
    if not appt_data.get("end_time"):
        if appt_data.get("start_time"):
             appt_data["end_time"] = appt_data["start_time"] + timedelta(minutes=15)

    db_appointment = models.Appointment(**appt_data)
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment

def get_appointments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Appointment).offset(skip).limit(limit).all()




def delete_appointment(db: Session, appointment_id: int):
    """
    Deletes an appointment by ID. Used for rollback if robot fails.
    """
    db_appointment = get_appointment(db, appointment_id)
    if db_appointment:
        db.delete(db_appointment)
        db.commit()
    return db_appointment

def get_appointment(db: Session, appointment_id: int):
    return db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

def get_appointments_for_range(db: Session, agenda: Optional[str], start_date: datetime.date, end_date: datetime.date):
    
    # Combine dates with min/max times to cover full days
    range_start = datetime.combine(start_date, time.min)
    range_end = datetime.combine(end_date, time.max)
    
    query = db.query(models.Appointment).filter(
        models.Appointment.start_time >= range_start,
        models.Appointment.start_time <= range_end
    )
    
    if agenda:
        query = query.filter(models.Appointment.agenda == agenda)
        
    return query.all()

def sync_appointments(db: Session, appointments: List[schemas.AppointmentCreate]):
    # 1. Determine Window
    sorted_appts = sorted(appointments, key=lambda x: x.start_time)
    min_time = sorted_appts[0].start_time
    max_time = sorted_appts[-1].start_time

    # 2. Get existing in window
    existing_in_window = db.query(models.Appointment).filter(
        models.Appointment.start_time >= min_time,
        models.Appointment.start_time <= max_time
    ).all()

    # 3. Identify Deletions
    incoming_keys = {(a.doctor_name, a.start_time) for a in appointments}

    deleted_count = 0
    for db_appt in existing_in_window:
        if (db_appt.doctor_name, db_appt.start_time) not in incoming_keys:
            db.delete(db_appt)
            deleted_count += 1
    
    # 4. Identify Creations
    created_count = 0
    existing_keys = {(a.doctor_name, a.start_time) for a in existing_in_window}

    for appt in appointments:
        if (appt.doctor_name, appt.start_time) not in existing_keys:
            create_appointment(db, appt)
            created_count += 1
    
    db.commit()
    
    return {
        "status": "success", 
        "deleted": deleted_count, 
        "created": created_count, 
        "window_start": min_time, 
        "window_end": max_time
    }
