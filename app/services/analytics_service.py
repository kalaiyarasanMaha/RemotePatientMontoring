import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.measurement import Measurement
from app.schemas.measurement import MeasurementResponse, MeasurementAggregate

class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_patient_vitals_summary(self, patient_id: int, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive vitals summary for a patient"""
        from app.crud.measurement import get_patient_measurements
        measurements = get_patient_measurements(self.db, patient_id, days)
        
        if not measurements:
            return {"error": "No measurements found for the specified period"}
        
        # Convert to DataFrame for analysis
        df = self._measurements_to_dataframe(measurements)
        
        summary = {
            "patient_id": patient_id,
            "time_period_days": days,
            "total_measurements": len(measurements),
            "vitals_summary": {},
            "trends": {},
            "anomalies": []
        }
        
        # Analyze each vital parameter
        vital_params = [
            'heart_rate', 'systolic_bp', 'diastolic_bp', 
            'blood_oxygen', 'temperature', 'respiratory_rate'
        ]
        
        for param in vital_params:
            if param in df.columns:
                param_data = df[param].dropna()
                if not param_data.empty:
                    summary["vitals_summary"][param] = {
                        "average": float(param_data.mean()),
                        "min": float(param_data.min()),
                        "max": float(param_data.max()),
                        "latest": float(param_data.iloc[-1]) if len(param_data) > 0 else None,
                        "std_dev": float(param_data.std())
                    }
                    
                    # Check trend
                    trend = self._analyze_parameter_trend(param_data)
                    summary["trends"][param] = trend
        
        # Check for anomalies
        summary["anomalies"] = self._detect_anomalies(df)
        
        # Calculate daily averages
        if 'measurement_time' in df.columns:
            df['date'] = pd.to_datetime(df['measurement_time']).dt.date
            daily_stats = {}
            
            for param in vital_params:
                if param in df.columns:
                    daily_avg = df.groupby('date')[param].mean().dropna()
                    if not daily_avg.empty:
                        daily_stats[param] = {
                            str(date): float(value) 
                            for date, value in daily_avg.items()
                        }
            
            summary["daily_averages"] = daily_stats
        
        return summary
    
    def _measurements_to_dataframe(self, measurements: List[MeasurementResponse]) -> pd.DataFrame:
        """Convert measurements to pandas DataFrame"""
        data = []
        for m in measurements:
            row = {
                'measurement_time': m.measurement_time,
                'heart_rate': m.heart_rate,
                'systolic_bp': m.systolic_bp,
                'diastolic_bp': m.diastolic_bp,
                'blood_oxygen': m.blood_oxygen,
                'temperature': m.temperature,
                'respiratory_rate': m.respiratory_rate,
                'blood_glucose': m.blood_glucose,
                'weight': m.weight,
                'height': m.height,
                'bmi': m.bmi,
                'steps': m.steps,
                'calories_burned': m.calories_burned,
                'distance': m.distance,
                'active_minutes': m.active_minutes
            }
            data.append(row)
        
        return pd.DataFrame(data)
    
    def _analyze_parameter_trend(self, data: pd.Series) -> Dict[str, Any]:
        """Analyze trend of a parameter over time"""
        if len(data) < 3:
            return {"trend": "insufficient_data", "confidence": 0}
        
        # Simple linear regression
        x = np.arange(len(data))
        y = data.values
        
        # Calculate slope
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # Determine trend direction
        if abs(slope) < 0.1:
            trend = "stable"
        elif slope > 0:
            trend = "increasing"
        else:
            trend = "decreasing"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "confidence": "high" if r_squared > 0.7 else "medium" if r_squared > 0.4 else "low"
        }
    
    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies in measurement data"""
        anomalies = []
        
        # Define normal ranges
        normal_ranges = {
            'heart_rate': (60, 100),
            'systolic_bp': (90, 140),
            'diastolic_bp': (60, 90),
            'blood_oxygen': (95, 100),
            'temperature': (36.0, 37.5),
            'respiratory_rate': (12, 20)
        }
        
        for param, (low, high) in normal_ranges.items():
            if param in df.columns:
                param_data = df[param].dropna()
                
                # Find values outside normal range
                outliers = param_data[(param_data < low) | (param_data > high)]
                
                for idx, value in outliers.items():
                    anomalies.append({
                        "parameter": param,
                        "value": float(value),
                        "normal_range": {"low": low, "high": high},
                        "timestamp": df.iloc[idx]['measurement_time'].isoformat() if 'measurement_time' in df.columns else None,
                        "severity": "high" if (
                            (param == 'blood_oxygen' and value < 92) or
                            (param == 'heart_rate' and (value < 40 or value > 150))
                        ) else "medium"
                    })
        
        return anomalies
    
    def predict_health_risk(self, patient_id: int) -> Dict[str, Any]:
        """Predict health risk based on historical data"""
        from app.crud.measurement import get_patient_measurements
        measurements = get_patient_measurements(self.db, patient_id, 30)  # 30 days of data
        
        if len(measurements) < 10:
            return {"error": "Insufficient data for prediction"}
        
        df = self._measurements_to_dataframe(measurements)
        
        risk_score = 0
        risk_factors = []
        
        # Analyze various risk factors
        vital_params = ['heart_rate', 'systolic_bp', 'diastolic_bp', 'blood_oxygen', 'temperature']
        
        for param in vital_params:
            if param in df.columns:
                param_data = df[param].dropna()
                if len(param_data) >= 5:
                    avg = param_data.mean()
                    std = param_data.std()
                    
                    # Check if consistently outside normal range
                    if param == 'heart_rate':
                        if avg > 90:
                            risk_score += 1
                            risk_factors.append(f"Elevated average heart rate: {avg:.1f} BPM")
                    elif param == 'systolic_bp':
                        if avg > 135:
                            risk_score += 2
                            risk_factors.append(f"Elevated systolic blood pressure: {avg:.1f} mmHg")
                    elif param == 'blood_oxygen':
                        if avg < 94:
                            risk_score += 3
                            risk_factors.append(f"Low blood oxygen saturation: {avg:.1f}%")
        
        # Check for high variability (instability)
        for param in vital_params:
            if param in df.columns:
                param_data = df[param].dropna()
                if len(param_data) >= 5:
                    cv = param_data.std() / param_data.mean() if param_data.mean() != 0 else 0
                    if cv > 0.2:  # High coefficient of variation
                        risk_score += 1
                        risk_factors.append(f"High variability in {param.replace('_', ' ')}")
        
        # Determine risk level
        if risk_score >= 5:
            risk_level = "high"
        elif risk_score >= 3:
            risk_level = "medium"
        elif risk_score >= 1:
            risk_level = "low"
        else:
            risk_level = "very_low"
        
        return {
            "patient_id": patient_id,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": self._generate_recommendations(risk_factors)
        }
    
    def _generate_recommendations(self, risk_factors: List[str]) -> List[str]:
        """Generate health recommendations based on risk factors"""
        recommendations = []
        
        for factor in risk_factors:
            if 'heart rate' in factor.lower():
                recommendations.append("Consider consulting a cardiologist for heart rate management.")
            elif 'blood pressure' in factor.lower():
                recommendations.append("Monitor blood pressure regularly and consider lifestyle modifications.")
            elif 'blood oxygen' in factor.lower():
                recommendations.append("Seek medical attention for low blood oxygen levels.")
            elif 'variability' in factor.lower():
                recommendations.append("Increased variability may indicate instability; consult with healthcare provider.")
        
        if not recommendations:
            recommendations.append("Continue with current monitoring regimen.")
        
        return recommendations