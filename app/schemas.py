from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AppointmentBase(BaseModel):
    doctor_name: str
    patient_name: str
    start_time: datetime
    end_time: datetime
    agenda: Optional[str] = None
    center: Optional[str] = None
    visit_type: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    end_time: Optional[datetime] = None
    trigger_robot: bool = False # set to True to execute the RPA robot immediately

class Appointment(AppointmentBase):
    id: int

    class Config:
        from_attributes = True
