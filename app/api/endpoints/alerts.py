from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import json
from app.models.alert import AlertStatus

from app.database import get_db
from app.crud import alert as crud_alert
from app.crud import patient as crud_patient
from app.schemas.alert import (
    AlertResponse, AlertCreate, AlertUpdate, 
    AlertAcknowledge, AlertResolve, AlertRuleCreate, AlertRuleResponse
)
from app.api.dependencies import get_current_user, require_clinician, get_alert_or_404
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["alerts"])

@router.get("/", response_model=List[AlertResponse])
def list_alerts(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    patient_id: Optional[int] = Query(None),
    alert_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    include_resolved: bool = Query(False),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all alerts (with filtering)"""
    alerts = crud_alert.get_alerts(
        db,
        skip=skip,
        limit=limit,
        patient_id=patient_id,
        alert_type=alert_type,
        severity=severity,
        status=status,
        include_resolved=include_resolved,
        start_date=start_date,
        end_date=end_date
    )
    # Convert alerts with deserialized alert_data
    return [crud_alert.format_alert_response(alert) for alert in alerts]

@router.get("/{alert_id}", response_model=AlertResponse)
def read_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alert details"""
    alert = crud_alert.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return crud_alert.format_alert_response(alert)

@router.post("/", response_model=AlertResponse, status_code=status.HTTP_201_CREATED)
def create_alert(
    alert: AlertCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Create a new alert (manual creation)"""
    # Verify patient exists
    patient = crud_patient.get_patient(db, alert.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {alert.patient_id} not found"
        )
    
    created_alert = crud_alert.create_alert(db, alert)
    return crud_alert.format_alert_response(created_alert)

@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    acknowledgment: AlertAcknowledge,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Acknowledge an alert"""
    alert = crud_alert.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot acknowledge a resolved alert"
        )
    
    acknowledged_alert = crud_alert.acknowledge_alert(db, alert_id, current_user["id"], acknowledgment)
    return crud_alert.format_alert_response(acknowledged_alert)

@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(
    alert_id: int,
    resolution: AlertResolve,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Resolve an alert"""
    alert = crud_alert.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    
    if alert.status == AlertStatus.RESOLVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alert is already resolved"
        )
    
    resolved_alert = crud_alert.resolve_alert(db, alert_id, current_user["id"], resolution)
    return crud_alert.format_alert_response(resolved_alert)

@router.put("/{alert_id}", response_model=AlertResponse)
def update_alert(
    alert_id: int,
    alert_update: AlertUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Update alert information"""
    updated_alert = crud_alert.update_alert(db, alert_id, alert_update)
    if not updated_alert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert with ID {alert_id} not found"
        )
    return crud_alert.format_alert_response(updated_alert)

@router.get("/stats/overall")
def get_alerts_overall_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get overall statistics about alerts"""
    return crud_alert.get_alert_stats(db, days)

@router.get("/active/count")
def get_active_alerts_count(
    patient_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get count of active alerts"""
    count = crud_alert.get_active_alerts_count(db, patient_id)
    return {"active_alerts_count": count}

# Alert Rules endpoints
@router.post("/rules/", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
def create_alert_rule(
    rule: AlertRuleCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Create a new alert rule (admin only)"""
    created_rule = crud_alert.create_alert_rule(db, rule, current_user["id"])
    return crud_alert.format_alert_rule_response(created_rule)

@router.get("/rules/", response_model=List[AlertRuleResponse])
def list_alert_rules(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all alert rules"""
    rules = crud_alert.get_alert_rules(db, skip=skip, limit=limit, is_active=is_active)
    return [crud_alert.format_alert_rule_response(rule) for rule in rules]

@router.get("/rules/{rule_id}", response_model=AlertRuleResponse)
def read_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get alert rule details"""
    rule = crud_alert.get_alert_rule(db, rule_id)
    if not rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found"
        )
    return crud_alert.format_alert_rule_response(rule)

@router.put("/rules/{rule_id}", response_model=AlertRuleResponse)
def update_alert_rule(
    rule_id: int,
    rule_update: dict,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Update alert rule"""
    updated_rule = crud_alert.update_alert_rule(db, rule_id, rule_update)
    if not updated_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found"
        )
    return crud_alert.format_alert_rule_response(updated_rule)

@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_alert_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_clinician)
):
    """Delete an alert rule"""
    if not crud_alert.delete_alert_rule(db, rule_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Alert rule with ID {rule_id} not found"
        )

@router.post("/test/measurement/{measurement_id}")
def test_measurement_for_alerts(
    measurement_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Test a measurement for potential alerts (for debugging)"""
    from app.crud.measurement import get_measurement
    
    measurement = get_measurement(db, measurement_id)
    if not measurement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Measurement with ID {measurement_id} not found"
        )
    
    alert_service = AlertService(db)
    alerts = alert_service.check_measurement_for_alerts(measurement)
    
    return {
        "measurement_id": measurement_id,
        "alerts_detected": len(alerts) if alerts else 0,
        "alerts": alerts if alerts else []
    }