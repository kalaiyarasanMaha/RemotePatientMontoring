from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.crud.patient import get_patient
from app.crud.device import get_device
from app.crud.measurement import get_measurement
from app.crud.alert import get_alert

def get_current_user():
    """Mock current user dependency - implement based on your auth system"""
    # In production, implement proper JWT token validation
    return {"id": 1, "username": "admin", "role": "admin"}

def require_admin(current_user: dict = Depends(get_current_user)):
    """Require admin role"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def require_clinician(current_user: dict = Depends(get_current_user)):
    """Require clinician role"""
    if current_user.get("role") not in ["admin", "clinician"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Clinician privileges required"
        )
    return current_user

def get_patient_or_404(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get patient or raise 404"""
    patient = get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return patient

def get_device_or_404(
    device_id: int,
    db: Session = Depends(get_db)
):
    """Get device or raise 404"""
    device = get_device(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    return device

def get_measurement_or_404(
    measurement_id: int,
    db: Session = Depends(get_db)
):
    """Get measurement or raise 404"""
    measurement = get_measurement(db, measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )
    return measurement

def get_alert_or_404(
    alert_id: int,
    db: Session = Depends(get_db)
):
    """Get alert or raise 404"""
    alert = get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return alert