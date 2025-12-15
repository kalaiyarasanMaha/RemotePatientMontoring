import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Remote Patient Monitoring Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "postgresql://neondb_owner:npg_7ycNS3vMiGDh@ep-purple-fire-addfbs7u-pooler.c-2.us-east-1.aws.neon.tech/patient_monitoring?sslmode=require&channel_binding=require"
    )
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Redis (for Celery)
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]
    
    # Alert thresholds (in seconds)
    HEART_RATE_ALERT_THRESHOLD_LOW: int = 40
    HEART_RATE_ALERT_THRESHOLD_HIGH: int = 120
    BLOOD_PRESSURE_SYSTOLIC_HIGH: int = 140
    BLOOD_PRESSURE_DIASTOLIC_HIGH: int = 90
    BLOOD_OXYGEN_LOW: int = 92
    TEMPERATURE_HIGH: float = 38.0
    
    class Config:
        env_file = ".env"

settings = Settings()