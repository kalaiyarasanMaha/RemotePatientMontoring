from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class DeviceType(str, enum.Enum):
    SMARTWATCH = "smartwatch"
    BLOOD_PRESSURE_MONITOR = "blood_pressure_monitor"
    GLUCOSE_METER = "glucose_meter"
    PULSE_OXIMETER = "pulse_oximeter"
    ECG_MONITOR = "ecg_monitor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    ACTIVITY_TRACKER = "activity_tracker"

class DeviceStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(100), unique=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    device_type = Column(Enum(DeviceType), nullable=False)
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100), unique=True)
    firmware_version = Column(String(50))
    last_sync_time = Column(DateTime(timezone=True))
    battery_level = Column(Integer)  # percentage
    status = Column(Enum(DeviceStatus), default=DeviceStatus.ACTIVE)
    calibration_date = Column(DateTime(timezone=True))
    calibration_due_date = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    patient = relationship("Patient", back_populates="devices")
    measurements = relationship("Measurement", back_populates="device", cascade="all, delete-orphan")