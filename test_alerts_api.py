#!/usr/bin/env python3
"""
Comprehensive Alert API Test Script
Tests all alert endpoints with sample data
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000"
HEADERS = {
    "Content-Type": "application/json",
}

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def make_request(method, endpoint, data=None, description=""):
    """Make HTTP request and return response"""
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=HEADERS)
        elif method == "POST":
            response = requests.post(url, json=data, headers=HEADERS)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=HEADERS)
        elif method == "DELETE":
            response = requests.delete(url, headers=HEADERS)
        
        if response.status_code in [200, 201, 204]:
            print_success(description)
            return response.status_code, response.json() if response.text else None
        else:
            print_error(f"{description} - Status: {response.status_code}")
            print(f"  Error: {response.text}")
            return response.status_code, None
    except Exception as e:
        print_error(f"{description} - Exception: {str(e)}")
        return None, None

# ============================================================================
# SETUP PHASE: Create test data
# ============================================================================
def setup_test_data():
    """Create patient, device, and measurement for testing"""
    print_header("SETUP PHASE: Creating Test Data")
    
    # 1. Create a patient
    print_info("Creating test patient...")
    patient_data = {
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1990-01-15T00:00:00Z",
        "gender": "male",
        "email": f"test_patient_{int(datetime.now().timestamp())}@example.com",
        "phone": "555-1234",
        "address": "123 Test St"
    }
    status_code, patient = make_request("POST", "/patients/", patient_data, "Create patient")
    if not patient:
        print_warning("Failed to create patient. Trying with existing patient ID 3...")
        patient_id = 3
    else:
        patient_id = patient.get('id')
    
    print_info(f"Using patient ID: {patient_id}")
    
    # 2. Create a device
    print_info("Creating test device...")
    device_data = {
        "device_id": f"TEST-DEVICE-{int(datetime.now().timestamp())}",
        "patient_id": patient_id,
        "device_type": "smartwatch",
        "manufacturer": "TestCorp",
        "model": "Model-X",
        "serial_number": f"SN-{int(datetime.now().timestamp())}",
        "firmware_version": "1.0.0"
    }
    status_code, device = make_request("POST", "/devices/", device_data, "Create device")
    if not device:
        print_warning("Failed to create device. Using device ID 1...")
        device_id = 1
    else:
        device_id = device.get('id')
    
    print_info(f"Using device ID: {device_id}")
    
    # 3. Create a measurement
    print_info("Creating test measurement...")
    measurement_data = {
        "patient_id": patient_id,
        "device_id": device_id,
        "measurement_time": datetime.now().isoformat() + "Z",
        "heart_rate": 95,  # Elevated heart rate to trigger alert
        "systolic_bp": 130,
        "diastolic_bp": 85,
        "blood_oxygen": 98,
        "temperature": 36.8,
        "respiratory_rate": 18,
        "blood_glucose": 6.5
    }
    status_code, measurement = make_request("POST", "/measurements/", measurement_data, "Create measurement")
    if not measurement:
        print_warning("Failed to create measurement. Using measurement ID 1...")
        measurement_id = 1
    else:
        measurement_id = measurement.get('id')
    
    print_info(f"Using measurement ID: {measurement_id}")
    
    return patient_id, device_id, measurement_id

# ============================================================================
# TEST 1: Create Alert
# ============================================================================
def test_create_alert(patient_id):
    print_header("TEST 1: Create Alert")
    
    alert_data = {
        "patient_id": patient_id,
        "alert_type": "heart_rate_high",
        "severity": "high",
        "title": "High Heart Rate Alert",
        "description": "Patient's heart rate exceeded safe limits",
        "alert_data": {
            "current_heart_rate": 120,
            "normal_range_max": 100,
            "duration_minutes": 15,
            "recommended_action": "Monitor and contact physician if persists"
        },
        "triggered_by_measurement_id": None
    }
    
    print_info("Payload:")
    print(json.dumps(alert_data, indent=2))
    
    status_code, alert = make_request("POST", "/alerts/", alert_data, "Create alert")
    
    if alert:
        print_info(f"\nAlert Details:")
        print(f"  ID: {alert.get('id')}")
        print(f"  Status: {alert.get('status')}")
        print(f"  Type: {alert.get('alert_type')}")
        print(f"  Severity: {alert.get('severity')}")
        return alert.get('id')
    return None

# ============================================================================
# TEST 2: List All Alerts
# ============================================================================
def test_list_alerts():
    print_header("TEST 2: List All Alerts")
    
    status_code, alerts = make_request("GET", "/alerts/", description="List all alerts")
    
    if alerts:
        print_info(f"Total alerts: {len(alerts)}\n")
        for alert in alerts[:3]:  # Show first 3
            print(f"  Alert ID {alert.get('id')}: {alert.get('title')} ({alert.get('status')})")
    
    return alerts

# ============================================================================
# TEST 3: Get Alert by ID
# ============================================================================
def test_get_alert(alert_id):
    print_header("TEST 3: Get Alert by ID")
    
    if not alert_id:
        print_warning("No alert ID provided, skipping test")
        return None
    
    status_code, alert = make_request("GET", f"/alerts/{alert_id}", description=f"Get alert {alert_id}")
    
    if alert:
        print_info(f"\nAlert Details:")
        for key in ['id', 'patient_id', 'alert_type', 'severity', 'status', 'title', 'description']:
            print(f"  {key}: {alert.get(key)}")
    
    return alert

# ============================================================================
# TEST 4: Acknowledge Alert
# ============================================================================
def test_acknowledge_alert(alert_id):
    print_header("TEST 4: Acknowledge Alert")
    
    if not alert_id:
        print_warning("No alert ID provided, skipping test")
        return None
    
    ack_data = {
        "acknowledgment_notes": "Alert reviewed by Dr. Smith. Patient monitoring continues."
    }
    
    print_info("Payload:")
    print(json.dumps(ack_data, indent=2))
    
    status_code, alert = make_request("POST", f"/alerts/{alert_id}/acknowledge", ack_data, 
                                      f"Acknowledge alert {alert_id}")
    
    if alert:
        print_info(f"\nUpdated Alert:")
        print(f"  Status: {alert.get('status')}")
        print(f"  Acknowledged By: {alert.get('acknowledged_by')}")
        print(f"  Acknowledged At: {alert.get('acknowledged_at')}")
        print(f"  Notes: {alert.get('acknowledgment_notes')}")
    
    return alert

# ============================================================================
# TEST 5: Resolve Alert
# ============================================================================
def test_resolve_alert(alert_id):
    print_header("TEST 5: Resolve Alert")
    
    if not alert_id:
        print_warning("No alert ID provided, skipping test")
        return None
    
    resolve_data = {
        "resolution_notes": "Heart rate returned to normal range. Patient stable."
    }
    
    print_info("Payload:")
    print(json.dumps(resolve_data, indent=2))
    
    status_code, alert = make_request("POST", f"/alerts/{alert_id}/resolve", resolve_data,
                                      f"Resolve alert {alert_id}")
    
    if alert:
        print_info(f"\nUpdated Alert:")
        print(f"  Status: {alert.get('status')}")
        print(f"  Resolved By: {alert.get('resolved_by')}")
        print(f"  Resolved At: {alert.get('resolved_at')}")
        print(f"  Resolution Notes: {alert.get('resolution_notes')}")
    
    return alert

# ============================================================================
# TEST 6: Create Alert Rule
# ============================================================================
def test_create_alert_rule():
    print_header("TEST 6: Create Alert Rule")
    
    rule_data = {
        "name": "High Heart Rate Rule",
        "alert_type": "heart_rate_high",
        "condition": {
            "parameter": "heart_rate",
            "operator": "greater_than",
            "value": 100,
            "duration_minutes": 5
        },
        "severity": "high",
        "is_active": True
    }
    
    print_info("Payload:")
    print(json.dumps(rule_data, indent=2))
    
    status_code, rule = make_request("POST", "/alerts/rules/", rule_data, "Create alert rule")
    
    if rule:
        print_info(f"\nAlert Rule Details:")
        print(f"  ID: {rule.get('id')}")
        print(f"  Name: {rule.get('name')}")
        print(f"  Type: {rule.get('alert_type')}")
        print(f"  Is Active: {rule.get('is_active')}")
        return rule.get('id')
    
    return None

# ============================================================================
# TEST 7: List Alert Rules
# ============================================================================
def test_list_alert_rules():
    print_header("TEST 7: List Alert Rules")
    
    status_code, rules = make_request("GET", "/alerts/rules/", description="List alert rules")
    
    if rules:
        print_info(f"Total rules: {len(rules)}\n")
        for rule in rules[:3]:  # Show first 3
            print(f"  Rule ID {rule.get('id')}: {rule.get('name')} (Active: {rule.get('is_active')})")
    
    return rules

# ============================================================================
# TEST 8: Test Measurement for Alerts
# ============================================================================
def test_measurement_for_alerts(measurement_id):
    print_header("TEST 8: Test Measurement for Alerts")
    
    if not measurement_id:
        print_warning("No measurement ID provided, skipping test")
        return None
    
    status_code, result = make_request("POST", f"/alerts/test/measurement/{measurement_id}",
                                       description=f"Test measurement {measurement_id} for alerts")
    
    if result:
        print_info(f"\nTest Results:")
        print(f"  Alerts Detected: {result.get('alerts_detected')}")
        if result.get('alerts'):
            print(f"  Alert Details:")
            for alert in result.get('alerts', []):
                print(f"    - {alert}")
    
    return result

# ============================================================================
# TEST 9: Get Active Alerts Count
# ============================================================================
def test_active_alerts_count(patient_id):
    print_header("TEST 9: Get Active Alerts Count")
    
    status_code, result = make_request("GET", f"/alerts/active/count?patient_id={patient_id}",
                                       description=f"Get active alerts count for patient {patient_id}")
    
    if result:
        print_info(f"Active Alerts Count: {result.get('active_alerts_count')}")
    
    return result

# ============================================================================
# TEST 10: Get Alert Statistics
# ============================================================================
def test_alert_statistics():
    print_header("TEST 10: Get Alert Statistics")
    
    status_code, stats = make_request("GET", "/alerts/stats/overall?days=7",
                                      description="Get alert statistics (last 7 days)")
    
    if stats:
        print_info(f"Alert Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    return stats

# ============================================================================
# MAIN EXECUTION
# ============================================================================
def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔" + "="*58 + "╗")
    print("║" + "ALERT API COMPREHENSIVE TEST SUITE".center(58) + "║")
    print("║" + f"Base URL: {BASE_URL}".center(58) + "║")
    print("╚" + "="*58 + "╝")
    print(f"{Colors.ENDC}")
    
    # Setup test data
    patient_id, device_id, measurement_id = setup_test_data()
    
    # Run all tests
    alert_id = test_create_alert(patient_id)
    
    test_list_alerts()
    
    test_get_alert(alert_id)
    
    test_acknowledge_alert(alert_id)
    
    # Create another alert to test resolve
    new_alert_id = test_create_alert(patient_id)
    test_resolve_alert(new_alert_id)
    
    rule_id = test_create_alert_rule()
    
    test_list_alert_rules()
    
    test_measurement_for_alerts(measurement_id)
    
    test_active_alerts_count(patient_id)
    
    test_alert_statistics()
    
    print_header("TEST SUITE COMPLETED")
    print_success("All alert API tests completed!")
    print_info(f"Patient ID: {patient_id}")
    print_info(f"Device ID: {device_id}")
    print_info(f"Measurement ID: {measurement_id}")
    print_info(f"Test Alert IDs: {alert_id}, {new_alert_id}")
    
if __name__ == "__main__":
    main()
