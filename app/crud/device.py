from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate

def get_device(db: Session, device_id: int) -> Optional[Device]:
    return db.query(Device).filter(Device.id == device_id).first()

def get_device_by_serial(db: Session, serial_number: str) -> Optional[Device]:
    return db.query(Device).filter(Device.serial_number == serial_number).first()

def get_device_by_device_id(db: Session, device_id_str: str) -> Optional[Device]:
    return db.query(Device).filter(Device.device_id == device_id_str).first()

def get_device_by_id_or_device_id(db: Session, identifier) -> Optional[Device]:
    """Get device by either database ID (int) or device_id (str)"""
    if isinstance(identifier, int):
        return get_device(db, identifier)
    else:
        return get_device_by_device_id(db, str(identifier))

def get_devices(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    patient_id: Optional[int] = None,
    status: Optional[str] = None
) -> List[Device]:
    query = db.query(Device)
    
    if patient_id:
        query = query.filter(Device.patient_id == patient_id)
    
    if status:
        query = query.filter(Device.status == status)
    
    return query.offset(skip).limit(limit).all()

def create_device(db: Session, device: DeviceCreate) -> Device:
    db_device = Device(**device.model_dump())
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_device(
    db: Session, 
    device_id: int, 
    device_update: DeviceUpdate
) -> Optional[Device]:
    db_device = get_device(db, device_id)
    if not db_device:
        return None
    
    update_data = device_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_device, field, value)
    
    db.commit()
    db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: int) -> bool:
    db_device = get_device(db, device_id)
    if not db_device:
        return False
    
    db.delete(db_device)
    db.commit()
    return True

def update_device_sync_time(db: Session, device_id: int) -> Optional[Device]:
    from datetime import datetime
    db_device = get_device(db, device_id)
    if not db_device:
        return None
    
    db_device.last_sync_time = datetime.utcnow()
    db.commit()
    db.refresh(db_device)
    return db_device

def get_patient_devices(db: Session, patient_id: int) -> List[Device]:
    return db.query(Device).filter(Device.patient_id == patient_id).all()

def get_device_stats(db: Session) -> dict:
    total_devices = db.query(Device).count()
    active_devices = db.query(Device).filter(Device.status == "active").count()
    
    # Devices by type
    from sqlalchemy import func
    device_types = db.query(
        Device.device_type, 
        func.count(Device.id).label('count')
    ).group_by(Device.device_type).all()
    
    device_type_stats = {device_type: count for device_type, count in device_types}
    
    return {
        "total_devices": total_devices,
        "active_devices": active_devices,
        "device_type_stats": device_type_stats
    }