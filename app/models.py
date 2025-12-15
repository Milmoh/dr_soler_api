from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    doctor_name = Column(String, index=True)  # Responsable
    patient_name = Column(String, index=True)
    start_time = Column(DateTime, index=True)
    end_time = Column(DateTime)
    agenda = Column(String, nullable=True)  # Optico-Optometria
    center = Column(String, nullable=True)  # Centro
    visit_type = Column(String, nullable=True)  # Tipo Visita

