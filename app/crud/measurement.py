from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy import desc, func
from app.models.measurement import Measurement
from app.schemas.measurement import MeasurementCreate, MeasurementUpdate

def get_measurement(db: Session, measurement_id: int) -> Optional[Measurement]:
    return db.query(Measurement).filter(Measurement.id == measurement_id).first()

def get_measurements(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    patient_id: Optional[int] = None,
    device_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[Measurement]:
    query = db.query(Measurement)
    
    if patient_id:
        query = query.filter(Measurement.patient_id == patient_id)
    
    if device_id:
        query = query.filter(Measurement.device_id == device_id)
    
    if start_date:
        query = query.filter(Measurement.measurement_time >= start_date)
    
    if end_date:
        query = query.filter(Measurement.measurement_time <= end_date)
    
    return query.order_by(desc(Measurement.measurement_time)).offset(skip).limit(limit).all()

def create_measurement(db: Session, measurement: MeasurementCreate) -> Measurement:
    # Calculate BMI if weight and height are provided
    measurement_data = measurement.model_dump()
    if measurement_data.get('weight') and measurement_data.get('height'):
        height_m = measurement_data['height'] / 100  # convert cm to m
        if height_m > 0:
            measurement_data['bmi'] = measurement_data['weight'] / (height_m ** 2)
    
    db_measurement = Measurement(**measurement_data)
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def create_measurement_from_dict(db: Session, measurement_dict: dict) -> Measurement:
    """Create measurement directly from dictionary (already resolved device_id)"""
    # Calculate BMI if weight and height are provided
    if measurement_dict.get('weight') and measurement_dict.get('height'):
        height_m = measurement_dict['height'] / 100  # convert cm to m
        if height_m > 0:
            measurement_dict['bmi'] = measurement_dict['weight'] / (height_m ** 2)
    
    db_measurement = Measurement(**measurement_dict)
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def update_measurement(
    db: Session, 
    measurement_id: int, 
    measurement_update: MeasurementUpdate
) -> Optional[Measurement]:
    db_measurement = get_measurement(db, measurement_id)
    if not db_measurement:
        return None
    
    update_data = measurement_update.dict(exclude_unset=True)
    
    # Recalculate BMI if weight or height is updated
    if 'weight' in update_data or 'height' in update_data:
        weight = update_data.get('weight', db_measurement.weight)
        height = update_data.get('height', db_measurement.height)
        if weight and height:
            height_m = height / 100
            if height_m > 0:
                update_data['bmi'] = weight / (height_m ** 2)
    
    for field, value in update_data.items():
        setattr(db_measurement, field, value)
    
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def delete_measurement(db: Session, measurement_id: int) -> bool:
    db_measurement = get_measurement(db, measurement_id)
    if not db_measurement:
        return False
    
    db.delete(db_measurement)
    db.commit()
    return True

def get_patient_measurements(
    db: Session, 
    patient_id: int, 
    days: int = 7
) -> List[Measurement]:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return db.query(Measurement).filter(
        Measurement.patient_id == patient_id,
        Measurement.measurement_time >= start_date,
        Measurement.measurement_time <= end_date
    ).order_by(desc(Measurement.measurement_time)).all()

def get_measurement_stats(
    db: Session, 
    patient_id: int, 
    parameter: str,
    days: int = 7
) -> Dict:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get basic stats
    stats = db.query(
        func.avg(getattr(Measurement, parameter)).label('average'),
        func.min(getattr(Measurement, parameter)).label('min'),
        func.max(getattr(Measurement, parameter)).label('max'),
        func.count(getattr(Measurement, parameter)).label('count')
    ).filter(
        Measurement.patient_id == patient_id,
        Measurement.measurement_time >= start_date,
        Measurement.measurement_time <= end_date,
        getattr(Measurement, parameter).isnot(None)
    ).first()
    
    # Get latest value
    latest = db.query(Measurement).filter(
        Measurement.patient_id == patient_id,
        getattr(Measurement, parameter).isnot(None)
    ).order_by(desc(Measurement.measurement_time)).first()
    
    latest_value = getattr(latest, parameter) if latest else None
    
    return {
        "parameter": parameter,
        "average": stats.average if stats.average else None,
        "min": stats.min if stats.min else None,
        "max": stats.max if stats.max else None,
        "count": stats.count,
        "latest": latest_value,
        "time_period_days": days
    }

def batch_create_measurements(db: Session, measurements: List[MeasurementCreate]) -> List[Measurement]:
    db_measurements = []
    for measurement in measurements:
        measurement_data = measurement.model_dump()
        # Calculate BMI if applicable
        if measurement_data.get('weight') and measurement_data.get('height'):
            height_m = measurement_data['height'] / 100
            if height_m > 0:
                measurement_data['bmi'] = measurement_data['weight'] / (height_m ** 2)
        
        db_measurement = Measurement(**measurement_data)
        db.add(db_measurement)
        db_measurements.append(db_measurement)
    
    db.commit()
    for measurement in db_measurements:
        db.refresh(measurement)
    
    return db_measurements

def batch_create_measurements_from_dicts(db: Session, measurement_dicts: List[dict]) -> List[Measurement]:
    """Create measurements in batch from dictionaries (already resolved device_ids)"""
    db_measurements = []
    for measurement_dict in measurement_dicts:
        # Calculate BMI if applicable
        if measurement_dict.get('weight') and measurement_dict.get('height'):
            height_m = measurement_dict['height'] / 100
            if height_m > 0:
                measurement_dict['bmi'] = measurement_dict['weight'] / (height_m ** 2)
        
        db_measurement = Measurement(**measurement_dict)
        db.add(db_measurement)
        db_measurements.append(db_measurement)
    
    db.commit()
    for measurement in db_measurements:
        db.refresh(measurement)
    
    return db_measurements