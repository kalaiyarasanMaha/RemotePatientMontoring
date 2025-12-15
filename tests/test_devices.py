# test_devices.py
import pytest

def test_register_device(client):
    """
    Test ID: TC-DEV-001
    Description: Register a new medical device
    Expected: Device created and returned
    """
    # Create patient first
    patient_response = client.post("/patients/", json={
        "first_name": "Device",
        "last_name": "Test",
        "date_of_birth": "1985-05-15T00:00:00Z",
        "gender": "female",
        "email": "device.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Arrange
    device_data = {
        "device_id": "TEST-DEVICE-001",
        "patient_id": test_patient["id"],
        "device_type": "smartwatch",
        "manufacturer": "TestCorp",
        "model": "TestModel 1000"
    }
    
    # Act
    response = client.post("/devices/", json=device_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == "TEST-DEVICE-001"
    assert data["patient_id"] == test_patient["id"]

def test_device_battery_update(client):
    """
    Test ID: TC-DEV-002
    Description: Update device battery level
    Expected: Device battery level updated
    """
    # Create patient and device first
    patient_response = client.post("/patients/", json={
        "first_name": "Battery",
        "last_name": "Test",
        "date_of_birth": "1985-05-15T00:00:00Z",
        "gender": "female",
        "email": "battery.test@example.com"
    })
    test_patient = patient_response.json()
    
    device_data = {
        "device_id": "BATTERY-TEST-001",
        "patient_id": test_patient["id"],
        "device_type": "blood_pressure_monitor",
        "manufacturer": "HealthCorp"
    }
    create_response = client.post("/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Act
    update_data = {"battery_level": 45}
    response = client.put(f"/devices/{device_id}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["battery_level"] == 45

def test_device_sync(client):
    """
    Test ID: TC-DEV-003
    Description: Sync a device
    Expected: Device sync timestamp updated
    """
    # Create patient and device first
    patient_response = client.post("/patients/", json={
        "first_name": "Sync",
        "last_name": "Test",
        "date_of_birth": "1985-05-15T00:00:00Z",
        "gender": "female",
        "email": "sync.test@example.com"
    })
    test_patient = patient_response.json()
    
    device_data = {
        "device_id": "SYNC-TEST-001",
        "patient_id": test_patient["id"],
        "device_type": "activity_tracker",
        "manufacturer": "FitnessCorp"
    }
    create_response = client.post("/devices/", json=device_data)
    device_identifier = create_response.json()["device_id"]
    
    # Act - Sync device using string identifier
    response = client.post(f"/devices/{device_identifier}/sync")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == device_identifier
    assert data["last_sync_time"] is not None

def test_list_devices(client):
    """
    Test ID: TC-DEV-004
    Description: List devices for a patient
    Expected: All devices for patient returned
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "List",
        "last_name": "Test",
        "date_of_birth": "1985-05-15T00:00:00Z",
        "gender": "female",
        "email": "list.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Arrange - Create multiple devices
    devices = []
    for i in range(3):
        device_data = {
            "device_id": f"LIST-TEST-{i:03d}",
            "patient_id": test_patient["id"],
            "device_type": "smartwatch",
            "manufacturer": "TestCorp"
        }
        response = client.post("/devices/", json=device_data)
        devices.append(response.json())
    
    # Act
    response = client.get(f"/devices/?patient_id={test_patient['id']}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    for device in data:
        assert device["patient_id"] == test_patient["id"]

def test_device_validation(client):
    """
    Test ID: TC-DEV-005
    Description: Test device validation
    Expected: Invalid devices rejected
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Validation",
        "last_name": "Test",
        "date_of_birth": "1985-05-15T00:00:00Z",
        "gender": "female",
        "email": "validation.test@example.com"
    })
    test_patient = patient_response.json()
    
    test_cases = [
        (
            {
                "device_id": "VALID-001",
                "patient_id": test_patient["id"],
                "device_type": "invalid_type"
            },
            422,
            "Invalid device type"
        ),
        (
            {
                "device_id": "VALID-002",
                "patient_id": 999999,
                "device_type": "smartwatch"
            },
            404,
            "Patient not found"
        )
    ]
    
    for data, expected_status, description in test_cases:
        response = client.post("/devices/", json=data)
        assert response.status_code == expected_status, f"Failed: {description}"
    """
    Test ID: TC-DEV-001
    Description: Register a new medical device
    Expected: Device created and returned
    """
    # Arrange
    device_data = {
        "device_id": "TEST-DEVICE-001",
        "patient_id": test_patient["id"],
        "device_type": "smartwatch",
        "manufacturer": "TestCorp",
        "model": "TestModel 1000"
    }
    
    # Act
    response = client.post("/devices/", json=device_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["device_id"] == "TEST-DEVICE-001"
    assert data["patient_id"] == test_patient["id"]

def test_device_battery_update(client):
    """
    Test ID: TC-DEV-002
    Description: Update device battery level
    Expected: Device battery level updated
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Battery",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "battery.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Arrange - Register device first
    device_data = {
        "device_id": "BATTERY-TEST-001",
        "patient_id": test_patient["id"],
        "device_type": "blood_pressure_monitor",
        "manufacturer": "HealthCorp"
    }
    create_response = client.post("/devices/", json=device_data)
    device_id = create_response.json()["id"]
    
    # Act
    update_data = {"battery_level": 45}
    response = client.put(f"/devices/{device_id}", json=update_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["battery_level"] == 45

def test_device_sync(client):
    """
    Test ID: TC-DEV-003
    Description: Sync a device
    Expected: Device sync timestamp updated
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Sync",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "sync.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Arrange - Register device first
    device_data = {
        "device_id": "SYNC-TEST-001",
        "patient_id": test_patient["id"],
        "device_type": "activity_tracker",
        "manufacturer": "FitnessCorp"
    }
    create_response = client.post("/devices/", json=device_data)
    device_identifier = create_response.json()["device_id"]
    
    # Act - Sync device using string identifier
    response = client.post(f"/devices/{device_identifier}/sync")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["device_id"] == device_identifier
    assert data["last_sync_time"] is not None

def test_list_devices(client):
    """
    Test ID: TC-DEV-004
    Description: List devices for a patient
    Expected: All devices for patient returned
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "List",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "list.test@example.com"
    })
    test_patient = patient_response.json()
    
    # Arrange - Create multiple devices
    devices = []
    for i in range(3):
        device_data = {
            "device_id": f"LIST-TEST-{i:03d}",
            "patient_id": test_patient["id"],
            "device_type": "smartwatch",
            "manufacturer": "TestCorp"
        }
        response = client.post("/devices/", json=device_data)
        devices.append(response.json())
    
    # Act
    response = client.get(f"/devices/?patient_id={test_patient['id']}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    for device in data:
        assert device["patient_id"] == test_patient["id"]

def test_device_validation(client):
    """
    Test ID: TC-DEV-005
    Description: Test device validation
    Expected: Invalid devices rejected
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Valid",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "valid.test@example.com"
    })
    test_patient = patient_response.json()
    
    test_cases = [
        (
            {
                "device_id": "VALID-001",
                "patient_id": test_patient["id"],
                "device_type": "invalid_type"
            },
            422,
            "Invalid device type"
        ),
        (
            {
                "device_id": "VALID-002",
                "patient_id": 999999,
                "device_type": "smartwatch"
            },
            404,
            "Patient not found"
        )
    ]
    
    for data, expected_status, description in test_cases:
        response = client.post("/devices/", json=data)
        assert response.status_code == expected_status, f"Failed: {description}"