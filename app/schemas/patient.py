from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

class PatientBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    date_of_birth: datetime
    gender: Gender
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    primary_physician_id: Optional[int] = None

class PatientCreate(PatientBase):
    pass

class PatientUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    emergency_contact_name: Optional[str] = Field(None, max_length=100)
    emergency_contact_phone: Optional[str] = Field(None, max_length=20)
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    allergies: Optional[str] = None
    primary_physician_id: Optional[int] = None
    is_active: Optional[bool] = None

class PatientInDB(PatientBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)

class PatientResponse(PatientInDB):
    pass