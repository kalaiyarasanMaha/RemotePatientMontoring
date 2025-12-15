from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.patient import Patient
from app.schemas.patient import PatientCreate, PatientUpdate

def get_patient(db: Session, patient_id: int) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.id == patient_id).first()

def get_patient_by_email(db: Session, email: str) -> Optional[Patient]:
    return db.query(Patient).filter(Patient.email == email).first()

def get_patients(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[Patient]:
    query = db.query(Patient)
    
    if is_active is not None:
        query = query.filter(Patient.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def create_patient(db: Session, patient: PatientCreate) -> Patient:
    db_patient = Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def update_patient(
    db: Session, 
    patient_id: int, 
    patient_update: PatientUpdate
) -> Optional[Patient]:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    update_data = patient_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_patient, field, value)
    
    db.commit()
    db.refresh(db_patient)
    return db_patient

def delete_patient(db: Session, patient_id: int) -> bool:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return False
    
    db.delete(db_patient)
    db.commit()
    return True

def deactivate_patient(db: Session, patient_id: int) -> Optional[Patient]:
    db_patient = get_patient(db, patient_id)
    if not db_patient:
        return None
    
    db_patient.is_active = False
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient_stats(db: Session) -> dict:
    total_patients = db.query(Patient).count()
    active_patients = db.query(Patient).filter(Patient.is_active == True).count()
    
    # Get patients by gender
    male_patients = db.query(Patient).filter(Patient.gender == "male").count()
    female_patients = db.query(Patient).filter(Patient.gender == "female").count()
    
    return {
        "total_patients": total_patients,
        "active_patients": active_patients,
        "male_patients": male_patients,
        "female_patients": female_patients,
        "other_gender_patients": total_patients - male_patients - female_patients
    }