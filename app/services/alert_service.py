from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.crud.alert import create_alert
from app.crud.measurement import get_patient_measurements
from app.schemas.alert import AlertCreate, AlertType, AlertSeverity
from app.schemas.measurement import MeasurementResponse
from app.config import settings

class AlertService:
    def __init__(self, db: Session):
        self.db = db
    
    def check_measurement_for_alerts(self, measurement: MeasurementResponse) -> Optional[AlertCreate]:
        """Check a single measurement for potential alerts"""
        alerts = []
        
        # Check heart rate
        if measurement.heart_rate is not None:
            if measurement.heart_rate > settings.HEART_RATE_ALERT_THRESHOLD_HIGH:
                alerts.append(self._create_heart_rate_high_alert(measurement))
            elif measurement.heart_rate < settings.HEART_RATE_ALERT_THRESHOLD_LOW:
                alerts.append(self._create_heart_rate_low_alert(measurement))
        
        # Check blood pressure
        if measurement.systolic_bp is not None or measurement.diastolic_bp is not None:
            if (measurement.systolic_bp and measurement.systolic_bp > settings.BLOOD_PRESSURE_SYSTOLIC_HIGH) or \
               (measurement.diastolic_bp and measurement.diastolic_bp > settings.BLOOD_PRESSURE_DIASTOLIC_HIGH):
                alerts.append(self._create_blood_pressure_high_alert(measurement))
        
        # Check blood oxygen
        if measurement.blood_oxygen is not None:
            if measurement.blood_oxygen < settings.BLOOD_OXYGEN_LOW:
                alerts.append(self._create_blood_oxygen_low_alert(measurement))
        
        # Check temperature
        if measurement.temperature is not None:
            if measurement.temperature > settings.TEMPERATURE_HIGH:
                alerts.append(self._create_temperature_high_alert(measurement))
        
        # Check for trends (requires historical data)
        trend_alerts = self._check_trend_alerts(measurement)
        if trend_alerts:
            alerts.extend(trend_alerts)
        
        # Create alerts in database
        created_alerts = []
        for alert in alerts:
            if alert:
                db_alert = create_alert(self.db, alert)
                created_alerts.append(db_alert)
        
        return created_alerts if created_alerts else None
    
    def _create_heart_rate_high_alert(self, measurement: MeasurementResponse) -> AlertCreate:
        return AlertCreate(
            patient_id=measurement.patient_id,
            alert_type=AlertType.HEART_RATE_HIGH,
            severity=AlertSeverity.HIGH if measurement.heart_rate > 150 else AlertSeverity.MEDIUM,
            title=f"High Heart Rate Alert: {measurement.heart_rate} BPM",
            description=f"Patient's heart rate is elevated above normal threshold.",
            alert_data={
                "measurement_id": measurement.id,
                "heart_rate": measurement.heart_rate,
                "threshold": settings.HEART_RATE_ALERT_THRESHOLD_HIGH,
                "timestamp": measurement.measurement_time.isoformat()
            },
            triggered_by_measurement_id=measurement.id
        )
    
    def _create_heart_rate_low_alert(self, measurement: MeasurementResponse) -> AlertCreate:
        return AlertCreate(
            patient_id=measurement.patient_id,
            alert_type=AlertType.HEART_RATE_LOW,
            severity=AlertSeverity.HIGH if measurement.heart_rate < 40 else AlertSeverity.MEDIUM,
            title=f"Low Heart Rate Alert: {measurement.heart_rate} BPM",
            description=f"Patient's heart rate is below normal threshold.",
            alert_data={
                "measurement_id": measurement.id,
                "heart_rate": measurement.heart_rate,
                "threshold": settings.HEART_RATE_ALERT_THRESHOLD_LOW,
                "timestamp": measurement.measurement_time.isoformat()
            },
            triggered_by_measurement_id=measurement.id
        )
    
    def _create_blood_pressure_high_alert(self, measurement: MeasurementResponse) -> AlertCreate:
        return AlertCreate(
            patient_id=measurement.patient_id,
            alert_type=AlertType.BLOOD_PRESSURE_HIGH,
            severity=AlertSeverity.HIGH if (
                measurement.systolic_bp and measurement.systolic_bp > 180
            ) or (
                measurement.diastolic_bp and measurement.diastolic_bp > 120
            ) else AlertSeverity.MEDIUM,
            title=f"High Blood Pressure Alert: {measurement.systolic_bp}/{measurement.diastolic_bp} mmHg",
            description=f"Patient's blood pressure is above normal threshold.",
            alert_data={
                "measurement_id": measurement.id,
                "systolic_bp": measurement.systolic_bp,
                "diastolic_bp": measurement.diastolic_bp,
                "threshold_systolic": settings.BLOOD_PRESSURE_SYSTOLIC_HIGH,
                "threshold_diastolic": settings.BLOOD_PRESSURE_DIASTOLIC_HIGH,
                "timestamp": measurement.measurement_time.isoformat()
            },
            triggered_by_measurement_id=measurement.id
        )
    
    def _create_blood_oxygen_low_alert(self, measurement: MeasurementResponse) -> AlertCreate:
        return AlertCreate(
            patient_id=measurement.patient_id,
            alert_type=AlertType.BLOOD_OXYGEN_LOW,
            severity=AlertSeverity.CRITICAL if measurement.blood_oxygen < 88 else AlertSeverity.HIGH,
            title=f"Low Blood Oxygen Alert: {measurement.blood_oxygen}%",
            description=f"Patient's blood oxygen level is below normal threshold.",
            alert_data={
                "measurement_id": measurement.id,
                "blood_oxygen": measurement.blood_oxygen,
                "threshold": settings.BLOOD_OXYGEN_LOW,
                "timestamp": measurement.measurement_time.isoformat()
            },
            triggered_by_measurement_id=measurement.id
        )
    
    def _create_temperature_high_alert(self, measurement: MeasurementResponse) -> AlertCreate:
        return AlertCreate(
            patient_id=measurement.patient_id,
            alert_type=AlertType.TEMPERATURE_HIGH,
            severity=AlertSeverity.HIGH if measurement.temperature > 39.0 else AlertSeverity.MEDIUM,
            title=f"High Temperature Alert: {measurement.temperature}°C",
            description=f"Patient's temperature is above normal threshold.",
            alert_data={
                "measurement_id": measurement.id,
                "temperature": measurement.temperature,
                "threshold": settings.TEMPERATURE_HIGH,
                "timestamp": measurement.measurement_time.isoformat()
            },
            triggered_by_measurement_id=measurement.id
        )
    
    def _check_trend_alerts(self, measurement: MeasurementResponse) -> list:
        """Check for alert conditions based on trends"""
        alerts = []
        
        # Get recent measurements for trend analysis
        recent_measurements = get_patient_measurements(self.db, measurement.patient_id, days=3)
        
        if len(recent_measurements) < 5:  # Need enough data for trend analysis
            return alerts
        
        # Check for rapid heart rate increase
        heart_rate_trend = self._analyze_trend(
            [m.heart_rate for m in recent_measurements if m.heart_rate is not None]
        )
        
        if heart_rate_trend == "rapid_increase" and measurement.heart_rate:
            alerts.append(
                AlertCreate(
                    patient_id=measurement.patient_id,
                    alert_type=AlertType.HEART_RATE_HIGH,
                    severity=AlertSeverity.MEDIUM,
                    title="Rapid Heart Rate Increase Detected",
                    description="Patient's heart rate has been increasing rapidly over the past few hours.",
                    alert_data={
                        "measurement_id": measurement.id,
                        "heart_rate": measurement.heart_rate,
                        "trend": "rapid_increase",
                        "timestamp": measurement.measurement_time.isoformat()
                    },
                    triggered_by_measurement_id=measurement.id
                )
            )
        
        return alerts
    
    def _analyze_trend(self, values: list) -> str:
        """Simple trend analysis"""
        if len(values) < 3:
            return "insufficient_data"
        
        # Calculate rate of change
        recent_values = values[-5:] if len(values) >= 5 else values
        if len(recent_values) < 3:
            return "insufficient_data"
        
        # Check if values are consistently increasing
        increasing = all(
            recent_values[i] < recent_values[i + 1] 
            for i in range(len(recent_values) - 1)
        )
        
        # Check if values are consistently decreasing
        decreasing = all(
            recent_values[i] > recent_values[i + 1] 
            for i in range(len(recent_values) - 1)
        )
        
        if increasing:
            return "increasing"
        elif decreasing:
            return "decreasing"
        else:
            return "stable"
    
    def check_device_offline_alerts(self, device_id: str, last_sync_time: datetime) -> Optional[AlertCreate]:
        """Check if device has been offline for too long"""
        time_since_sync = datetime.utcnow() - last_sync_time
        
        # Alert if device hasn't synced in 24 hours
        if time_since_sync.total_seconds() > 24 * 3600:
            # This would require device/patient mapping
            # For now, return a generic alert structure
            return AlertCreate(
                patient_id=1,  # Would need to get from device
                alert_type=AlertType.DEVICE_OFFLINE,
                severity=AlertSeverity.MEDIUM,
                title=f"Device Offline Alert: {device_id}",
                description=f"Device has not synced data for {int(time_since_sync.total_seconds() / 3600)} hours.",
                alert_data={
                    "device_id": device_id,
                    "last_sync_time": last_sync_time.isoformat(),
                    "hours_offline": int(time_since_sync.total_seconds() / 3600)
                }
            )
        
        return None