# test_alerts.py
import pytest

def test_create_alert(client):
    """
    Test ID: TC-ALT-001
    Description: Create a manual alert
    Expected: Alert created and returned
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Alert",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "alert.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Arrange
    alert_data = {
        "patient_id": test_patient["id"],
        "alert_type": "heart_rate_high",
        "severity": "high",
        "title": "High Heart Rate Alert",
        "description": "Patient heart rate exceeds normal range",
        "alert_data": {
            "current_hr": 125,
            "threshold": 100
        }
    }
    
    # Act
    response = client.post("/alerts/", json=alert_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["alert_type"] == "heart_rate_high"
    assert data["severity"] == "high"
    assert data["patient_id"] == test_patient["id"]
    assert data["status"] == "active"

def test_alert_acknowledgment(client):
    """
    Test ID: TC-ALT-002
    Description: Acknowledge an active alert
    Expected: Alert status changes to acknowledged
    """
    # Create patient and alert
    patient_response = client.post("/patients/", json={
        "first_name": "Ack",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "ack.test@example.com"
    })
    test_patient = patient_response.json()
    
    alert_data = {
        "patient_id": test_patient["id"],
        "alert_type": "blood_pressure_high",
        "severity": "medium",
        "title": "High Blood Pressure"
    }
    create_response = client.post("/alerts/", json=alert_data)
    alert_id = create_response.json()["id"]
    
    # Act
    ack_data = {"acknowledgment_notes": "Monitoring patient closely"}
    response = client.post(f"/alerts/{alert_id}/acknowledge", json=ack_data)
    
    # Assert
    assert response.status_code == 200
    alert = response.json()
    assert alert["status"] == "acknowledged"
    assert alert["acknowledgment_notes"] == "Monitoring patient closely"
    assert alert["acknowledged_at"] is not None

def test_alert_resolution(client):
    """
    Test ID: TC-ALT-003
    Description: Resolve an acknowledged alert
    Expected: Alert status changes to resolved
    """
    # Create patient and alert
    patient_response = client.post("/patients/", json={
        "first_name": "Resolve",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "resolve.test@example.com"
    })
    test_patient = patient_response.json()
    
    alert_data = {
        "patient_id": test_patient["id"],
        "alert_type": "temperature_high",
        "severity": "medium",
        "title": "High Temperature"
    }
    create_response = client.post("/alerts/", json=alert_data)
    alert_id = create_response.json()["id"]
    
    # Acknowledge first
    client.post(f"/alerts/{alert_id}/acknowledge", json={})
    
    # Act - Resolve
    resolve_data = {"resolution_notes": "Patient fever resolved"}
    response = client.post(f"/alerts/{alert_id}/resolve", json=resolve_data)
    
    # Assert
    assert response.status_code == 200
    alert = response.json()
    assert alert["status"] == "resolved"
    assert alert["resolution_notes"] == "Patient fever resolved"
    assert alert["resolved_at"] is not None

def test_list_alerts(client):
    """
    Test ID: TC-ALT-004
    Description: List alerts with filtering
    Expected: Alerts returned with filters applied
    """
    # Create patient and alerts
    patient_response = client.post("/patients/", json={
        "first_name": "List",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "list.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Create some test alerts
    for i in range(3):
        alert_data = {
            "patient_id": test_patient["id"],
            "alert_type": "heart_rate_high",
            "severity": "high",
            "title": f"Alert {i}"
        }
        client.post("/alerts/", json=alert_data)
    
    # Act
    response = client.get(f"/alerts/?patient_id={test_patient['id']}")
    
    # Assert
    assert response.status_code == 200
    alerts = response.json()
    assert len(alerts) > 0
    for alert in alerts:
        assert alert["patient_id"] == test_patient["id"]

def test_get_alert(client):
    """
    Test ID: TC-ALT-005
    Description: Get a specific alert by ID
    Expected: Correct alert returned
    """
    # Create patient and alert
    patient_response = client.post("/patients/", json={
        "first_name": "Get",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "get.test@example.com"
    })
    test_patient = patient_response.json()
    
    alert_data = {
        "patient_id": test_patient["id"],
        "alert_type": "blood_oxygen_low",
        "severity": "critical",
        "title": "Low Blood Oxygen"
    }
    create_response = client.post("/alerts/", json=alert_data)
    alert_id = create_response.json()["id"]
    
    # Act
    response = client.get(f"/alerts/{alert_id}")
    
    # Assert
    assert response.status_code == 200
    alert = response.json()
    assert alert["id"] == alert_id
    assert alert["alert_type"] == "blood_oxygen_low"
    assert alert["severity"] == "critical"

def test_create_alert_rule(client):
    """
    Test ID: TC-ALT-006
    Description: Create an alert rule
    Expected: Rule created with correct condition handling
    """
    # Arrange
    rule_data = {
        "name": "BP Alert Rule",
        "alert_type": "blood_pressure_high",
        "condition": {
            "parameter": "systolic_bp",
            "operator": "greater_than",
            "threshold": 160
        },
        "severity": "high",
        "is_active": True
    }
    
    # Act
    response = client.post("/alerts/rules/", json=rule_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "BP Alert Rule"
    assert data["alert_type"] == "blood_pressure_high"
    assert data["condition"]["threshold"] == 160
    assert data["is_active"] is True

def test_list_alert_rules(client):
    """
    Test ID: TC-ALT-007
    Description: List alert rules
    Expected: All active rules returned
    """
    # Create a rule first
    rule_data = {
        "name": "Test Rule",
        "alert_type": "heart_rate_high",
        "condition": {"threshold": 120},
        "severity": "high",
        "is_active": True
    }
    client.post("/alerts/rules/", json=rule_data)
    
    # Act
    response = client.get("/alerts/rules/?is_active=true")
    
    # Assert
    assert response.status_code == 200
    rules = response.json()
    assert len(rules) > 0
    for rule in rules:
        assert rule["is_active"] is True

def test_get_alert_rule(client):
    """
    Test ID: TC-ALT-008
    Description: Get a specific alert rule
    Expected: Correct rule returned with condition
    """
    # Create a rule
    rule_data = {
        "name": "Get Rule Test",
        "alert_type": "temperature_high",
        "condition": {
            "parameter": "temperature",
            "threshold": 38.5
        },
        "severity": "medium",
        "is_active": True
    }
    create_response = client.post("/alerts/rules/", json=rule_data)
    rule_id = create_response.json()["id"]
    
    # Act
    response = client.get(f"/alerts/rules/{rule_id}")
    
    # Assert
    assert response.status_code == 200
    rule = response.json()
    assert rule["id"] == rule_id
    assert rule["name"] == "Get Rule Test"
    assert rule["condition"] is not None
    assert isinstance(rule["condition"], dict)
