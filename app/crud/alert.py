from sqlalchemy.orm import Session
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy import desc, func, or_
from app.models.alert import Alert, AlertRule, AlertStatus
from app.schemas.alert import AlertCreate, AlertUpdate, AlertAcknowledge, AlertResolve, AlertRuleCreate
import json

def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.id == alert_id).first()

def format_alert_response(alert: Alert) -> dict:
    """Convert Alert ORM object to response dict with deserialized alert_data and enum strings"""
    return {
        'id': alert.id,
        'patient_id': alert.patient_id,
        'alert_type': alert.alert_type.value if hasattr(alert.alert_type, 'value') else alert.alert_type,
        'severity': alert.severity.value if hasattr(alert.severity, 'value') else alert.severity,
        'title': alert.title,
        'description': alert.description,
        'alert_data': json.loads(alert.alert_data) if alert.alert_data else None,
        'status': alert.status.value if hasattr(alert.status, 'value') else alert.status,
        'acknowledged_by': alert.acknowledged_by,
        'acknowledged_at': alert.acknowledged_at,
        'acknowledgment_notes': alert.acknowledgment_notes,
        'resolved_by': alert.resolved_by,
        'resolved_at': alert.resolved_at,
        'resolution_notes': alert.resolution_notes,
        'triggered_by_measurement_id': alert.triggered_by_measurement_id,
        'created_at': alert.created_at,
        'updated_at': getattr(alert, 'updated_at', None)
    }

def format_alert_rule_response(rule: AlertRule) -> dict:
    """Convert AlertRule ORM object to response dict with deserialized condition"""
    return {
        'id': rule.id,
        'name': rule.name,
        'alert_type': rule.alert_type.value if hasattr(rule.alert_type, 'value') else rule.alert_type,
        'condition': json.loads(rule.condition) if rule.condition else None,
        'severity': rule.severity.value if hasattr(rule.severity, 'value') else rule.severity,
        'is_active': rule.is_active,
        'created_by': rule.created_by,
        'created_at': rule.created_at,
        'updated_at': getattr(rule, 'updated_at', None)
    }

def get_alerts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    patient_id: Optional[int] = None,
    alert_type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    include_resolved: bool = False
) -> List[Alert]:
    query = db.query(Alert)
    
    if patient_id:
        query = query.filter(Alert.patient_id == patient_id)
    
    if alert_type:
        query = query.filter(Alert.alert_type == alert_type)
    
    if severity:
        query = query.filter(Alert.severity == severity)
    
    if status:
        query = query.filter(Alert.status == status)
    elif not include_resolved:
        query = query.filter(Alert.status != AlertStatus.RESOLVED, Alert.status != AlertStatus.DISMISSED)
    
    if start_date:
        query = query.filter(Alert.created_at >= start_date)
    
    if end_date:
        query = query.filter(Alert.created_at <= end_date)
    
    return query.order_by(desc(Alert.created_at)).offset(skip).limit(limit).all()

def create_alert(db: Session, alert: AlertCreate) -> Alert:
    alert_data = alert.model_dump()
    # Convert alert_data dict to JSON string
    if alert_data.get('alert_data'):
        alert_data['alert_data'] = json.dumps(alert_data['alert_data'])
    db_alert = Alert(**alert_data)
    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)
    return db_alert

def update_alert(
    db: Session, 
    alert_id: int, 
    alert_update: AlertUpdate
) -> Optional[Alert]:
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    
    update_data = alert_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_alert, field, value)
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

def acknowledge_alert(
    db: Session, 
    alert_id: int, 
    user_id: int,
    acknowledgment: AlertAcknowledge
) -> Optional[Alert]:
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    
    db_alert.status = AlertStatus.ACKNOWLEDGED
    db_alert.acknowledged_by = user_id
    db_alert.acknowledged_at = datetime.utcnow()
    db_alert.acknowledgment_notes = acknowledgment.acknowledgment_notes
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

def resolve_alert(
    db: Session, 
    alert_id: int, 
    user_id: int,
    resolution: AlertResolve
) -> Optional[Alert]:
    db_alert = get_alert(db, alert_id)
    if not db_alert:
        return None
    
    db_alert.status = AlertStatus.RESOLVED
    db_alert.resolved_by = user_id
    db_alert.resolved_at = datetime.utcnow()
    db_alert.resolution_notes = resolution.resolution_notes
    
    db.commit()
    db.refresh(db_alert)
    return db_alert

def get_active_alerts_count(db: Session, patient_id: Optional[int] = None) -> int:
    query = db.query(Alert).filter(
        or_(
            Alert.status == AlertStatus.ACTIVE,
            Alert.status == AlertStatus.ACKNOWLEDGED
        )
    )
    
    if patient_id:
        query = query.filter(Alert.patient_id == patient_id)
    
    return query.count()

def get_alert_stats(db: Session, days: int = 7) -> Dict:
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Total alerts
    total_alerts = db.query(Alert).filter(
        Alert.created_at >= start_date,
        Alert.created_at <= end_date
    ).count()
    
    # Alerts by type
    alert_types = db.query(
        Alert.alert_type, 
        func.count(Alert.id).label('count')
    ).filter(
        Alert.created_at >= start_date,
        Alert.created_at <= end_date
    ).group_by(Alert.alert_type).all()
    
    # Alerts by status
    alert_statuses = db.query(
        Alert.status, 
        func.count(Alert.id).label('count')
    ).filter(
        Alert.created_at >= start_date,
        Alert.created_at <= end_date
    ).group_by(Alert.status).all()
    
    # Alerts by severity
    alert_severities = db.query(
        Alert.severity, 
        func.count(Alert.id).label('count')
    ).filter(
        Alert.created_at >= start_date,
        Alert.created_at <= end_date
    ).group_by(Alert.severity).all()
    
    return {
        "time_period_days": days,
        "total_alerts": total_alerts,
        "alerts_by_type": {alert_type: count for alert_type, count in alert_types},
        "alerts_by_status": {status: count for status, count in alert_statuses},
        "alerts_by_severity": {severity: count for severity, count in alert_severities}
    }

# Alert Rules CRUD
def get_alert_rule(db: Session, rule_id: int) -> Optional[AlertRule]:
    return db.query(AlertRule).filter(AlertRule.id == rule_id).first()

def get_alert_rules(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    is_active: Optional[bool] = None
) -> List[AlertRule]:
    query = db.query(AlertRule)
    
    if is_active is not None:
        query = query.filter(AlertRule.is_active == is_active)
    
    return query.offset(skip).limit(limit).all()

def create_alert_rule(db: Session, rule: AlertRuleCreate, created_by: int) -> AlertRule:
    rule_data = rule.model_dump()
    # Convert condition dict to JSON string
    if rule_data.get('condition'):
        rule_data['condition'] = json.dumps(rule_data['condition'])
    db_rule = AlertRule(**rule_data)
    db_rule.created_by = created_by
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def update_alert_rule(
    db: Session, 
    rule_id: int, 
    rule_update: Dict
) -> Optional[AlertRule]:
    db_rule = get_alert_rule(db, rule_id)
    if not db_rule:
        return None
    
    for field, value in rule_update.items():
        if field == 'condition' and isinstance(value, dict):
            # Convert condition dict to JSON string
            value = json.dumps(value)
        setattr(db_rule, field, value)
    
    db.commit()
    db.refresh(db_rule)
    return db_rule

def delete_alert_rule(db: Session, rule_id: int) -> bool:
    db_rule = get_alert_rule(db, rule_id)
    if not db_rule:
        return False
    
    db.delete(db_rule)
    db.commit()
    return True