import pytest

def test_create_patient(client):
    """Test creating a new patient"""
    patient_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-01-01T00:00:00Z",
        "gender": "male",
        "email": "john.doe@example.com"
    }
    
    response = client.post("/patients/", json=patient_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["is_active"] == True
    assert "id" in data

def test_get_patient(client):
    """Test getting patient details"""
    # First create a patient
    patient_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1990-05-15T00:00:00Z",
        "gender": "female",
        "email": "jane.smith@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]
    
    # Get the patient
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["first_name"] == "Jane"
    assert data["email"] == "jane.smith@example.com"

def test_update_patient(client):
    """Test updating patient information"""
    # Create a patient first
    patient_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "date_of_birth": "1975-08-20T00:00:00Z",
        "gender": "male",
        "email": "bob.johnson@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]
    
    # Update the patient
    update_data = {
        "first_name": "Robert",
        "phone": "+1122334455"
    }
    
    response = client.put(f"/patients/{patient_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Robert"
    assert data["phone"] == "+1122334455"
    assert data["last_name"] == "Johnson"  # Should remain unchanged

def test_list_patients(client):
    """Test listing all patients"""
    # Create some patients first
    for i in range(2):
        patient_data = {
            "first_name": f"Patient{i}",
            "last_name": "Test",
            "date_of_birth": "1980-01-01T00:00:00Z",
            "gender": "male",
            "email": f"patient{i}@example.com"
        }
        client.post("/patients/", json=patient_data)
    
    response = client.get("/patients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Test with pagination
    response = client.get("/patients/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

def test_create_duplicate_patient_email(client):
    """Test creating patient with duplicate email"""
    patient_data = {
        "first_name": "Alice",
        "last_name": "Brown",
        "date_of_birth": "1985-03-10T00:00:00Z",
        "gender": "female",
        "email": "alice.unique@example.com"
    }
    
    # First creation should succeed
    response1 = client.post("/patients/", json=patient_data)
    assert response1.status_code == 201
    
    # Second creation with same email should fail
    response2 = client.post("/patients/", json=patient_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_get_nonexistent_patient(client):
    """Test getting a patient that doesn't exist"""
    response = client.get("/patients/99999")
    assert response.status_code == 404

def test_patient_measurements(client):
    """Test getting patient measurements"""
    # First create a patient
    patient_data = {
        "first_name": "Measure",
        "last_name": "Test",
        "date_of_birth": "1990-01-01T00:00:00Z",
        "gender": "male",
        "email": "measure.test@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]
    
    # Get measurements (should be empty initially)
    response = client.get(f"/patients/{patient_id}/measurements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_patient_alerts(client):
    """Test getting patient alerts"""
    # Create a patient
    patient_data = {
        "first_name": "AlertTest",
        "last_name": "Patient",
        "date_of_birth": "1990-01-01T00:00:00Z",
        "gender": "male",
        "email": "alerttest.patient@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    assert create_response.status_code == 201
    patient_id = create_response.json()["id"]
    
    # Get alerts (should be empty initially)
    response = client.get(f"/patients/{patient_id}/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_patient_stats(client):
    """Test getting patient statistics"""
    response = client.get("/patients/stats/overall")
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    assert isinstance(data["total_patients"], int)