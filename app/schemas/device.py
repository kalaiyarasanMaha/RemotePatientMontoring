from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class DeviceType(str, Enum):
    SMARTWATCH = "smartwatch"
    BLOOD_PRESSURE_MONITOR = "blood_pressure_monitor"
    GLUCOSE_METER = "glucose_meter"
    PULSE_OXIMETER = "pulse_oximeter"
    ECG_MONITOR = "ecg_monitor"
    TEMPERATURE_SENSOR = "temperature_sensor"
    ACTIVITY_TRACKER = "activity_tracker"

class DeviceStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    RETIRED = "retired"

class DeviceBase(BaseModel):
    device_id: str = Field(..., min_length=1, max_length=100)
    patient_id: int
    device_type: DeviceType
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    serial_number: Optional[str] = Field(None, max_length=100)
    firmware_version: Optional[str] = Field(None, max_length=50)
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    status: DeviceStatus = DeviceStatus.ACTIVE
    notes: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_type: Optional[DeviceType] = None
    manufacturer: Optional[str] = Field(None, max_length=100)
    model: Optional[str] = Field(None, max_length=100)
    battery_level: Optional[int] = Field(None, ge=0, le=100)
    status: Optional[DeviceStatus] = None
    last_sync_time: Optional[datetime] = None
    calibration_date: Optional[datetime] = None
    calibration_due_date: Optional[datetime] = None
    notes: Optional[str] = None

class DeviceInDB(DeviceBase):
    id: int
    last_sync_time: Optional[datetime] = None
    calibration_date: Optional[datetime] = None
    calibration_due_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class DeviceResponse(DeviceInDB):
    pass