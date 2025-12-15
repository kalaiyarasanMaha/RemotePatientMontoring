from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(10), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    emergency_contact_name = Column(String(100))
    emergency_contact_phone = Column(String(20))
    medical_history = Column(Text)
    current_medications = Column(Text)
    allergies = Column(Text)
    primary_physician_id = Column(Integer, ForeignKey("users.id"))
    primary_physician = relationship("User", foreign_keys=[primary_physician_id])
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    devices = relationship("Device", back_populates="patient", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")