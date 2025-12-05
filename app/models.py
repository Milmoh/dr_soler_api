from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, index=True)
    patient_name = Column(String, index=True)
    date = Column(DateTime)
    description = Column(String)
    is_available = Column(Boolean, default=True)
