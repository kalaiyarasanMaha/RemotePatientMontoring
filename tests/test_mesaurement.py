# test_measurements.py
import pytest
from datetime import datetime

def test_measurement_creation(client):
    """
    Test ID: TC-MEA-001
    Description: Create a new measurement
    Expected: Measurement created and returned
    """
    # Create patient first
    patient_response = client.post("/patients/", json={
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1980-01-01T00:00:00Z",
        "gender": "male",
        "email": "test.patient.mea@example.com"
    })
    test_patient = patient_response.json()
    
    # Create device
    device_response = client.post("/devices/", json={
        "device_id": "TEST-DEVICE-001",
        "patient_id": test_patient["id"],
        "device_type": "smartwatch",
        "manufacturer": "TestCorp"
    })
    test_device = device_response.json()
    
    # Arrange
    measurement_data = {
        "patient_id": test_patient["id"],
        "device_id": test_device["device_id"],
        "measurement_time": datetime.utcnow().isoformat() + "Z",
        "heart_rate": 75,
        "systolic_bp": 120,
        "diastolic_bp": 80,
        "blood_oxygen": 98
    }
    
    # Act
    response = client.post("/measurements/", json=measurement_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["heart_rate"] == 75
    assert data["patient_id"] == test_patient["id"]
    assert data["device_id"] == test_device["device_id"]  # Should return string identifier

def test_measurement_validation(client):
    """
    Test ID: TC-MEA-002
    Description: Test measurement validation rules
    Expected: Invalid measurements rejected
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Valid",
        "last_name": "Test",
        "date_of_birth": "1970-01-01T00:00:00Z",
        "gender": "male",
        "email": "valid.mea@example.com"
    })
    test_patient = patient_response.json()
    
    test_cases = [
        # (data, expected_status, description)
        (
            {
                "patient_id": test_patient["id"],
                "device_id": "INVALID-DEVICE",
                "heart_rate": 300,  # Impossible heart rate
                "measurement_time": datetime.utcnow().isoformat() + "Z"
            },
            404,
            "Device not found"
        ),
        (
            {
                "patient_id": test_patient["id"],
                "device_id": "TEST-DEVICE-001",
                "blood_oxygen": 150,  # Impossible SpO2
                "measurement_time": datetime.utcnow().isoformat() + "Z"
            },
            422,
            "Blood oxygen > 100%"
        ),
        (
            {
                "patient_id": 999999,
                "device_id": "TEST-DEVICE-001",
                "heart_rate": 80,
                "measurement_time": datetime.utcnow().isoformat() + "Z"
            },
            404,
            "Patient not found"
        )
    ]
    
    for data, expected_status, description in test_cases:
        response = client.post("/measurements/", json=data)
        assert response.status_code == expected_status, f"Failed: {description}"

def test_batch_measurement_creation(client):
    """
    Test ID: TC-MEA-003
    Description: Create multiple measurements in batch
    Expected: All measurements created successfully
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Batch",
        "last_name": "Test",
        "date_of_birth": "1980-01-01T00:00:00Z",
        "gender": "male",
        "email": "batch.test.mea@example.com"
    })
    test_patient = patient_response.json()
    
    # Create device
    device_response = client.post("/devices/", json={
        "device_id": "BATCH-TEST-001",
        "patient_id": test_patient["id"],
        "device_type": "smartwatch",
        "manufacturer": "TestCorp"
    })
    test_device = device_response.json()
    
    # Arrange
    measurements_data = [
        {
            "patient_id": test_patient["id"],
            "device_id": test_device["device_id"],
            "measurement_time": datetime.utcnow().isoformat() + "Z",
            "heart_rate": 70,
            "systolic_bp": 118
        },
        {
            "patient_id": test_patient["id"],
            "device_id": test_device["device_id"],
            "measurement_time": datetime.utcnow().isoformat() + "Z",
            "heart_rate": 75,
            "systolic_bp": 120
        },
        {
            "patient_id": test_patient["id"],
            "device_id": test_device["device_id"],
            "measurement_time": datetime.utcnow().isoformat() + "Z",
            "heart_rate": 80,
            "systolic_bp": 122
        }
    ]
    
    # Act
    response = client.post("/measurements/batch", json=measurements_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 3
    for measurement in data:
        assert measurement["device_id"] == test_device["device_id"]  # String identifier
        assert measurement["patient_id"] == test_patient["id"]

def test_list_measurements(client):
    """
    Test ID: TC-MEA-004
    Description: List measurements with filtering
    Expected: Measurements returned with correct filters applied
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "List",
        "last_name": "Test",
        "date_of_birth": "1980-01-01T00:00:00Z",
        "gender": "male",
        "email": "list.test.mea@example.com"
    })
    test_patient = patient_response.json()
    
    # Create device
    device_response = client.post("/devices/", json={
        "device_id": "LIST-MEA-001",
        "patient_id": test_patient["id"],
        "device_type": "smartwatch",
        "manufacturer": "TestCorp"
    })
    test_device = device_response.json()
    
    # Create some measurements first
    measurement_data = {
        "patient_id": test_patient["id"],
        "device_id": test_device["device_id"],
        "measurement_time": datetime.utcnow().isoformat() + "Z",
        "heart_rate": 85,
        "systolic_bp": 125
    }
    client.post("/measurements/", json=measurement_data)
    
    # Act - List all measurements
    response = client.get(f"/measurements/?patient_id={test_patient['id']}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for measurement in data:
        assert measurement["patient_id"] == test_patient["id"]
        assert measurement["device_id"] == test_device["device_id"]  # String identifier

def test_get_measurement(client):
    """
    Test ID: TC-MEA-005
    Description: Get a specific measurement by ID
    Expected: Correct measurement returned
    """
    # Create patient
    patient_response = client.post("/patients/", json={
        "first_name": "Get",
        "last_name": "Test",
        "date_of_birth": "1980-01-01T00:00:00Z",
        "gender": "male",
        "email": "get.test.mea@example.com"
    })
    test_patient = patient_response.json()
    
    # Create device
    device_response = client.post("/devices/", json={
        "device_id": "GET-MEA-001",
        "patient_id": test_patient["id"],
        "device_type": "smartwatch",
        "manufacturer": "TestCorp"
    })
    test_device = device_response.json()
    
    # Create a measurement
    measurement_data = {
        "patient_id": test_patient["id"],
        "device_id": test_device["device_id"],
        "measurement_time": datetime.utcnow().isoformat() + "Z",
        "heart_rate": 90,
        "systolic_bp": 128
    }
    create_response = client.post("/measurements/", json=measurement_data)
    measurement_id = create_response.json()["id"]
    
    # Act
    response = client.get(f"/measurements/{measurement_id}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == measurement_id
    assert data["heart_rate"] == 90
    assert data["device_id"] == test_device["device_id"]  # String identifier
