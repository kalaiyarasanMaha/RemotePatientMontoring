from sqlalchemy import Column, Integer, Float, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Measurement(Base):
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    
    # Vital signs
    heart_rate = Column(Float)  # BPM
    systolic_bp = Column(Float)  # mmHg
    diastolic_bp = Column(Float)  # mmHg
    blood_oxygen = Column(Float)  #percentage
    temperature = Column(Float)  # Celsius
    respiratory_rate = Column(Float)  # breaths per minute
    blood_glucose = Column(Float)  # mg/dL
    weight = Column(Float)  # kg
    height = Column(Float)  # cm
    bmi = Column(Float)  # kg/m²
    
    # Activity data
    steps = Column(Integer)
    calories_burned = Column(Float)
    distance = Column(Float)  # km
    active_minutes = Column(Integer)
    
    # ECG data (could be stored as JSON or file path)
    ecg_data = Column(Text)  # JSON string or file reference
    ecg_analysis = Column(Text)  # JSON analysis results
    
    # Metadata
    measurement_time = Column(DateTime(timezone=True), nullable=False)
    timezone = Column(String(50))
    latitude = Column(Float)
    longitude = Column(Float)
    accuracy = Column(Float)  # measurement accuracy
    data_source = Column(String(50))  # device, manual, etc.
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="measurements")
    device = relationship("Device", back_populates="measurements")