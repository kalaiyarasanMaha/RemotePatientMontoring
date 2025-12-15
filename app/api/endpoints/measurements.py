from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import datetime, timedelta

from app.database import get_db
from app.crud import measurement as crud_measurement
from app.crud import patient as crud_patient
from app.crud import device as crud_device
from app.schemas.measurement import MeasurementCreate, MeasurementUpdate, MeasurementResponse
from app.api.dependencies import get_current_user, get_measurement_or_404
from app.services.alert_service import AlertService

router = APIRouter(prefix="/measurements", tags=["measurements"])

@router.post("/", response_model=MeasurementResponse, status_code=status.HTTP_201_CREATED)
def create_measurement(
    measurement: MeasurementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new measurement"""
    # Verify patient exists
    patient = crud_patient.get_patient(db, measurement.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {measurement.patient_id} not found"
        )
    
    # Verify device exists and is assigned to patient
    device = crud_device.get_device_by_id_or_device_id(db, measurement.device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {measurement.device_id} not found"
        )
    
    if device.patient_id != measurement.patient_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device is not assigned to this patient"
        )
    
    # Create measurement with resolved device database ID
    measurement_dict = measurement.model_dump()
    measurement_dict['device_id'] = device.id
    created_measurement = crud_measurement.create_measurement_from_dict(db, measurement_dict)
    
    # Check for alerts
    alert_service = AlertService(db)
    alerts = alert_service.check_measurement_for_alerts(created_measurement)
    
    # Update response with alert info
    # Return device's string identifier instead of database ID
    response_data = {
        'id': created_measurement.id,
        'patient_id': created_measurement.patient_id,
        'device_id': device.device_id,  # Use the device's string identifier
        'heart_rate': created_measurement.heart_rate,
        'systolic_bp': created_measurement.systolic_bp,
        'diastolic_bp': created_measurement.diastolic_bp,
        'blood_oxygen': created_measurement.blood_oxygen,
        'temperature': created_measurement.temperature,
        'respiratory_rate': created_measurement.respiratory_rate,
        'blood_glucose': created_measurement.blood_glucose,
        'weight': created_measurement.weight,
        'height': created_measurement.height,
        'bmi': created_measurement.bmi,
        'steps': created_measurement.steps,
        'calories_burned': created_measurement.calories_burned,
        'distance': created_measurement.distance,
        'active_minutes': created_measurement.active_minutes,
        'measurement_time': created_measurement.measurement_time,
        'timezone': created_measurement.timezone,
        'latitude': created_measurement.latitude,
        'longitude': created_measurement.longitude,
        'accuracy': created_measurement.accuracy,
        'data_source': created_measurement.data_source,
        'notes': created_measurement.notes,
        'created_at': created_measurement.created_at,
        'updated_at': getattr(created_measurement, 'updated_at', None)
    }
    if alerts:
        response_data["alerts_generated"] = len(alerts)
        response_data["alert_ids"] = [alert.id for alert in alerts]
    
    return response_data

@router.post("/batch", response_model=List[MeasurementResponse], status_code=status.HTTP_201_CREATED)
def create_measurements_batch(
    measurements: List[MeasurementCreate],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create multiple measurements in batch"""
    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No measurements provided"
        )
    
    # Validate all patients and devices
    for measurement in measurements:
        patient = crud_patient.get_patient(db, measurement.patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient with ID {measurement.patient_id} not found"
            )
        
        device = crud_device.get_device_by_id_or_device_id(db, measurement.device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {measurement.device_id} not found"
            )
        
        if device.patient_id != measurement.patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Device {measurement.device_id} is not assigned to patient {measurement.patient_id}"
            )
    
    # Resolve all device IDs to database IDs before batch creation
    resolved_measurements = []
    device_map = {}  # Track device_id -> device object for response
    for measurement in measurements:
        device = crud_device.get_device_by_id_or_device_id(db, measurement.device_id)
        measurement_dict = measurement.model_dump()
        measurement_dict['device_id'] = device.id
        resolved_measurements.append(measurement_dict)
        device_map[device.id] = device  # Store device object for response
    
    # Create measurements
    created_measurements = crud_measurement.batch_create_measurements_from_dicts(db, resolved_measurements)
    
    # Check for alerts
    alert_service = AlertService(db)
    all_alerts = []
    for measurement in created_measurements:
        alerts = alert_service.check_measurement_for_alerts(measurement)
        if alerts:
            all_alerts.extend(alerts)
    
    # Add alert info to response
    response_data = []
    for measurement in created_measurements:
        # Get the original device identifier from the device_map
        device = device_map.get(measurement.device_id)
        device_identifier = device.device_id if device else measurement.device_id
        
        measurement_dict = {
            'id': measurement.id,
            'patient_id': measurement.patient_id,
            'device_id': device_identifier,  # Use device's string identifier
            'heart_rate': measurement.heart_rate,
            'systolic_bp': measurement.systolic_bp,
            'diastolic_bp': measurement.diastolic_bp,
            'blood_oxygen': measurement.blood_oxygen,
            'temperature': measurement.temperature,
            'respiratory_rate': measurement.respiratory_rate,
            'blood_glucose': measurement.blood_glucose,
            'weight': measurement.weight,
            'height': measurement.height,
            'bmi': measurement.bmi,
            'steps': measurement.steps,
            'calories_burned': measurement.calories_burned,
            'distance': measurement.distance,
            'active_minutes': measurement.active_minutes,
            'measurement_time': measurement.measurement_time,
            'timezone': measurement.timezone,
            'latitude': measurement.latitude,
            'longitude': measurement.longitude,
            'accuracy': measurement.accuracy,
            'data_source': measurement.data_source,
            'notes': measurement.notes,
            'created_at': measurement.created_at,
            "has_alerts": any(
                alert.triggered_by_measurement_id == measurement.id 
                for alert in all_alerts
            )
        }
        response_data.append(measurement_dict)
    
    return response_data

@router.get("/{measurement_id}", response_model=MeasurementResponse)
def read_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get measurement details"""
    measurement = crud_measurement.get_measurement(db, measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )
    
    # Get device to return string identifier
    device = crud_device.get_device(db, measurement.device_id)
    
    response_data = {
        'id': measurement.id,
        'patient_id': measurement.patient_id,
        'device_id': device.device_id if device else measurement.device_id,
        'heart_rate': measurement.heart_rate,
        'systolic_bp': measurement.systolic_bp,
        'diastolic_bp': measurement.diastolic_bp,
        'blood_oxygen': measurement.blood_oxygen,
        'temperature': measurement.temperature,
        'respiratory_rate': measurement.respiratory_rate,
        'blood_glucose': measurement.blood_glucose,
        'weight': measurement.weight,
        'height': measurement.height,
        'bmi': measurement.bmi,
        'steps': measurement.steps,
        'calories_burned': measurement.calories_burned,
        'distance': measurement.distance,
        'active_minutes': measurement.active_minutes,
        'measurement_time': measurement.measurement_time,
        'timezone': measurement.timezone,
        'latitude': measurement.latitude,
        'longitude': measurement.longitude,
        'accuracy': measurement.accuracy,
        'data_source': measurement.data_source,
        'notes': measurement.notes,
        'created_at': measurement.created_at,
        'updated_at': getattr(measurement, 'updated_at', None)
    }
    
    return response_data

@router.put("/{measurement_id}", response_model=MeasurementResponse)
def update_measurement(
    measurement_id: int,
    measurement_update: MeasurementUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update measurement information"""
    updated_measurement = crud_measurement.update_measurement(db, measurement_id, measurement_update)
    if not updated_measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )
    return updated_measurement

@router.delete("/{measurement_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a measurement"""
    if not crud_measurement.delete_measurement(db, measurement_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )

@router.get("/", response_model=List[MeasurementResponse])
def list_measurements(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    patient_id: Optional[int] = Query(None),
    device_id: Optional[Union[int, str]] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all measurements (with filtering)"""
    # Resolve device_id if provided
    resolved_device_id = None
    if device_id:
        device = crud_device.get_device_by_id_or_device_id(db, device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Device with ID {device_id} not found"
            )
        resolved_device_id = device.id
    
    measurements = crud_measurement.get_measurements(
        db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        device_id=resolved_device_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Format responses with device string identifiers
    response_data = []
    for measurement in measurements:
        device = crud_device.get_device(db, measurement.device_id)
        measurement_dict = {
            'id': measurement.id,
            'patient_id': measurement.patient_id,
            'device_id': device.device_id if device else measurement.device_id,
            'heart_rate': measurement.heart_rate,
            'systolic_bp': measurement.systolic_bp,
            'diastolic_bp': measurement.diastolic_bp,
            'blood_oxygen': measurement.blood_oxygen,
            'temperature': measurement.temperature,
            'respiratory_rate': measurement.respiratory_rate,
            'blood_glucose': measurement.blood_glucose,
            'weight': measurement.weight,
            'height': measurement.height,
            'bmi': measurement.bmi,
            'steps': measurement.steps,
            'calories_burned': measurement.calories_burned,
            'distance': measurement.distance,
            'active_minutes': measurement.active_minutes,
            'measurement_time': measurement.measurement_time,
            'timezone': measurement.timezone,
            'latitude': measurement.latitude,
            'longitude': measurement.longitude,
            'accuracy': measurement.accuracy,
            'data_source': measurement.data_source,
            'notes': measurement.notes,
            'created_at': measurement.created_at,
            'updated_at': getattr(measurement, 'updated_at', None)
        }
        response_data.append(measurement_dict)
    
    return response_data

@router.get("/stats/patient/{patient_id}")
def get_patient_measurement_stats(
    patient_id: int,
    parameter: str = Query(..., description="Parameter to analyze (heart_rate, systolic_bp, etc.)"),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get statistics for a specific parameter for a patient"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    # Validate parameter
    valid_parameters = [
        'heart_rate', 'systolic_bp', 'diastolic_bp', 'blood_oxygen',
        'temperature', 'respiratory_rate', 'blood_glucose', 'weight',
        'height', 'bmi', 'steps', 'calories_burned', 'distance', 'active_minutes'
    ]
    
    if parameter not in valid_parameters:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid parameter. Must be one of: {', '.join(valid_parameters)}"
        )
    
    return crud_measurement.get_measurement_stats(db, patient_id, parameter, days)

@router.get("/recent/patient/{patient_id}")
def get_recent_patient_measurements(
    patient_id: int,
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get recent measurements for a patient (last X hours)"""
    patient = crud_patient.get_patient(db, patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found"
        )
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(hours=hours)
    
    measurements = crud_measurement.get_measurements(
        db,
        skip=0,
        limit=limit,
        patient_id=patient_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Format responses with device string identifiers
    response_data = []
    for measurement in measurements:
        device = crud_device.get_device(db, measurement.device_id)
        measurement_dict = {
            'id': measurement.id,
            'patient_id': measurement.patient_id,
            'device_id': device.device_id if device else measurement.device_id,
            'heart_rate': measurement.heart_rate,
            'systolic_bp': measurement.systolic_bp,
            'diastolic_bp': measurement.diastolic_bp,
            'blood_oxygen': measurement.blood_oxygen,
            'temperature': measurement.temperature,
            'respiratory_rate': measurement.respiratory_rate,
            'blood_glucose': measurement.blood_glucose,
            'weight': measurement.weight,
            'height': measurement.height,
            'bmi': measurement.bmi,
            'steps': measurement.steps,
            'calories_burned': measurement.calories_burned,
            'distance': measurement.distance,
            'active_minutes': measurement.active_minutes,
            'measurement_time': measurement.measurement_time,
            'timezone': measurement.timezone,
            'latitude': measurement.latitude,
            'longitude': measurement.longitude,
            'accuracy': measurement.accuracy,
            'data_source': measurement.data_source,
            'notes': measurement.notes,
            'created_at': measurement.created_at,
            'updated_at': getattr(measurement, 'updated_at', None)
        }
        response_data.append(measurement_dict)
    
    return response_data