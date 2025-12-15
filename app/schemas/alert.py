from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class AlertType(str, Enum):
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

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class AlertBase(BaseModel):
    patient_id: int
    alert_type: AlertType
    severity: AlertSeverity
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    alert_data: Optional[dict] = None

class AlertCreate(AlertBase):
    triggered_by_measurement_id: Optional[int] = None

class AlertUpdate(BaseModel):
    status: Optional[AlertStatus] = None
    acknowledgment_notes: Optional[str] = None
    resolution_notes: Optional[str] = None

class AlertAcknowledge(BaseModel):
    acknowledgment_notes: Optional[str] = None

class AlertResolve(BaseModel):
    resolution_notes: Optional[str] = None

class AlertInDB(AlertBase):
    id: int
    status: AlertStatus
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    acknowledgment_notes: Optional[str] = None
    resolved_by: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolution_notes: Optional[str] = None
    triggered_by_measurement_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class AlertResponse(AlertInDB):
    pass

class AlertRuleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    alert_type: AlertType
    condition: dict  # JSON condition
    severity: AlertSeverity
    is_active: bool = True

class AlertRuleCreate(AlertRuleBase):
    pass

class AlertRuleResponse(AlertRuleBase):
    id: int
    created_by: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)