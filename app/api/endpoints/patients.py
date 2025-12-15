from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.database import get_db
from app.crud import patient as crud_patient
from app.crud import measurement as crud_measurement
from app.crud import alert as crud_alert
from app.crud import device as crud_device
from app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from app.schemas.measurement import MeasurementResponse, MeasurementAggregate
from app.schemas.alert import AlertResponse
from app.schemas.device import DeviceResponse
from app.api.dependencies import get_current_user, require_clinician, get_patient_or_404
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/patients", tags=["patients"])

@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Create a new patient (clinician/admin only)"""
    # Check if patient with email already exists
    existing_patient = crud_patient.get_patient_by_email(db, patient.email)
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient with this email already exists"
        )
    
    return crud_patient.create_patient(db, patient)

@router.get("/{patient_id}", response_model=PatientResponse)
def read_patient(
    patient: PatientResponse = Depends(get_patient_or_404)
):
    """Get patient details"""
    return patient

@router.put("/{patient_id}", response_model=PatientResponse)
def update_patient(
    patient_id: int,
    patient_update: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Update patient information"""
    updated_patient = crud_patient.update_patient(db, patient_id, patient_update)
    if not updated_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    return updated_patient

@router.delete("/{patient_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Delete a patient"""
    if not crud_patient.delete_patient(db, patient_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )

@router.get("/{patient_id}/measurements", response_model=List[MeasurementResponse])
def get_patient_measurements(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get measurements for a specific patient"""
    # Verify patient exists
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return crud_measurement.get_measurements(
        db, 
        skip=skip, 
        limit=limit,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/{patient_id}/measurements/stats")
def get_patient_measurement_stats(
    patient_id: int,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get statistics for patient measurements"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Get stats for key parameters
    parameters = ['heart_rate', 'systolic_bp', 'diastolic_bp', 'blood_oxygen', 'temperature']
    stats = []
    
    for param in parameters:
        stat = crud_measurement.get_measurement_stats(db, patient_id, param, days)
        stats.append(stat)
    
    return {
        "patient_id": patient_id,
        "time_period_days": days,
        "parameter_stats": stats
    }

@router.get("/{patient_id}/alerts", response_model=List[AlertResponse])
def get_patient_alerts(
    patient_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    include_resolved: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alerts for a specific patient"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    return crud_alert.get_alerts(
        db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        status=status,
        severity=severity,
        include_resolved=include_resolved
    )

@router.get("/{patient_id}/devices", response_model=List[DeviceResponse])
def get_patient_devices(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get devices assigned to a patient"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    return crud_device.get_patient_devices(db, patient_id)

@router.get("/{patient_id}/analytics/summary")
def get_patient_analytics_summary(
    patient_id: int,
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive analytics summary for a patient"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    analytics_service = AnalyticsService(db)
    return analytics_service.get_patient_vitals_summary(patient_id, days)

@router.get("/{patient_id}/analytics/risk-assessment")
def get_patient_risk_assessment(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get health risk assessment for a patient"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    analytics_service = AnalyticsService(db)
    return analytics_service.predict_health_risk(patient_id)

@router.get("/", response_model=List[PatientResponse])
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all patients (with pagination)"""
    return crud_patient.get_patients(db, skip=skip, limit=limit, is_active=is_active)

@router.get("/stats/overall")
def get_patients_overall_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get overall statistics about patients"""
    return crud_patient.get_patient_stats(db)