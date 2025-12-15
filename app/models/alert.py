# app/models/alert.py - Updated version without user foreign keys
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class AlertType(str, enum.Enum):
    HEART_RATE_HIGH = "heart_rate_high"
    HEART_RATE_LOW = "heart_rate_low"
    BLOOD_PRESSURE_HIGH = "blood_pressure_high"
    BLOOD_OXYGEN_LOW = "blood_oxygen_low"
    TEMPERATURE_HIGH = "temperature_high"
    GLUCOSE_HIGH = "glucose_high"
    GLUCOSE_LOW = "glucose_low"
    FALL_DETECTED = "fall_detected"
    DEVICE_OFFLINE = "device_offline"
    MEDICATION_REMINDER = "medication_reminder"
    APPOINTMENT_REMINDER = "appointment_reminder"

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    severity = Column(Enum(AlertSeverity), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    alert_data = Column(Text)  # JSON with details
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE)
    
    # Acknowledgment info (without foreign key for now)
    acknowledged_by = Column(Integer, nullable=True)
    acknowledged_at = Column(DateTime(timezone=True))
    acknowledgment_notes = Column(Text)
    
    # Resolution info (without foreign key for now)
    resolved_by = Column(Integer, nullable=True)
    resolved_at = Column(DateTime(timezone=True))
    resolution_notes = Column(Text)
    
    # Metadata
    triggered_by_measurement_id = Column(Integer, ForeignKey("measurements.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="alerts")
    measurement = relationship("Measurement")

class AlertRule(Base):
    __tablename__ = "alert_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    condition = Column(Text)  # JSON condition
    severity = Column(Enum(AlertSeverity), nullable=False)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=True)  # Changed from ForeignKey
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())