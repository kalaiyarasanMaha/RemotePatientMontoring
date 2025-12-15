from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union

from app.database import get_db
from app.crud import device as crud_device
from app.crud import patient as crud_patient
from app.crud import measurement as crud_measurement
from app.schemas.device import DeviceCreate, DeviceUpdate, DeviceResponse
from app.schemas.measurement import MeasurementResponse
from app.api.dependencies import get_current_user, require_clinician, get_device_or_404
from app.services.alert_service import AlertService

router = APIRouter(prefix="/devices", tags=["devices"])

@router.post("/", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(
    device: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Register a new device and assign to patient"""
    # Check if patient exists
    patient = crud_patient.get_patient(db, device.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {device.patient_id} not found"
        )
    
    # Check if device ID already exists
    existing_device = crud_device.get_device_by_device_id(db, device.device_id)
    if existing_device:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Device with this ID already exists"
        )
    
    # Check if serial number already exists (if provided)
    if device.serial_number:
        existing_serial = crud_device.get_device_by_serial(db, device.serial_number)
        if existing_serial:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Device with this serial number already exists"
            )
    
    return crud_device.create_device(db, device)

@router.get("/{device_id}", response_model=DeviceResponse)
def read_device(
    device: DeviceResponse = Depends(get_device_or_404)
):
    """Get device details"""
    return device

@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(
    device_id: int,
    device_update: DeviceUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Update device information"""
    updated_device = crud_device.update_device(db, device_id, device_update)
    if not updated_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    return updated_device

@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Delete a device"""
    if not crud_device.delete_device(db, device_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )

@router.get("/{device_id}/measurements", response_model=List[MeasurementResponse])
def get_device_measurements(
    device_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get measurements from a specific device"""
    device = crud_device.get_device(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    return crud_measurement.get_measurements(
        db, 
        skip=skip, 
        limit=limit,
        device_id=device_id
    )

@router.post("/{device_id}/sync")
def sync_device(
    device_id: Union[int, str],
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update device sync timestamp (accepts both integer DB ID and string device_id)"""
    # Try to resolve device by either database ID or device_id string
    device = crud_device.get_device_by_id_or_device_id(db, device_id)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Device with ID {device_id} not found"
        )
    
    updated_device = crud_device.update_device_sync_time(db, device.id)
    
    # Check for device offline alerts
    alert_service = AlertService(db)
    offline_alert = alert_service.check_device_offline_alerts(
        updated_device.device_id,
        updated_device.last_sync_time
    )
    
    response = {
        "message": "Device sync time updated",
        "device_id": updated_device.device_id,
        "last_sync_time": updated_device.last_sync_time.isoformat()
    }
    
    if offline_alert:
        response["alert_cleared"] = True
    
    return response

@router.get("/", response_model=List[DeviceResponse])
def list_devices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    patient_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all devices (with optional filtering)"""
    return crud_device.get_devices(
        db, 
        skip=skip, 
        limit=limit,
        patient_id=patient_id,
        status=status
    )

@router.get("/stats/overall")
def get_devices_overall_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get overall statistics about devices"""
    return crud_device.get_device_stats(db)