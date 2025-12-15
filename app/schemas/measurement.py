from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Union
from datetime import datetime

class MeasurementBase(BaseModel):
    patient_id: int
    device_id: Union[int, str]
    measurement_time: datetime
    
    # Vital signs
    heart_rate: Optional[float] = Field(None, ge=0, le=300)
    systolic_bp: Optional[float] = Field(None, ge=0, le=300)
    diastolic_bp: Optional[float] = Field(None, ge=0, le=200)
    blood_oxygen: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=20, le=50)
    respiratory_rate: Optional[float] = Field(None, ge=0, le=100)
    blood_glucose: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    
    # Activity data
    steps: Optional[int] = Field(None, ge=0)
    calories_burned: Optional[float] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    active_minutes: Optional[int] = Field(None, ge=0)
    
    # Metadata
    timezone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    accuracy: Optional[float] = None
    data_source: Optional[str] = None
    notes: Optional[str] = None

class MeasurementCreate(MeasurementBase):
    pass

class MeasurementUpdate(BaseModel):
    heart_rate: Optional[float] = Field(None, ge=0, le=300)
    systolic_bp: Optional[float] = Field(None, ge=0, le=300)
    diastolic_bp: Optional[float] = Field(None, ge=0, le=200)
    blood_oxygen: Optional[float] = Field(None, ge=0, le=100)
    temperature: Optional[float] = Field(None, ge=20, le=50)
    respiratory_rate: Optional[float] = Field(None, ge=0, le=100)
    blood_glucose: Optional[float] = Field(None, ge=0)
    weight: Optional[float] = Field(None, ge=0)
    height: Optional[float] = Field(None, ge=0)
    steps: Optional[int] = Field(None, ge=0)
    calories_burned: Optional[float] = Field(None, ge=0)
    distance: Optional[float] = Field(None, ge=0)
    active_minutes: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class MeasurementInDB(MeasurementBase):
    id: int
    bmi: Optional[float] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MeasurementResponse(MeasurementInDB):
    pass

class MeasurementAggregate(BaseModel):
    parameter: str
    average: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    latest: Optional[float] = None
    trend: Optional[str] = None  # increasing, decreasing, stable