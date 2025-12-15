import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from app.main import app
from app.database import Base, get_db
from app.config import settings

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Drop tables
    Base.metadata.drop_all(bind=engine)

def test_create_patient(setup_database):
    """Test creating a new patient"""
    patient_data = {
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1980-01-01T00:00:00",
        "gender": "male",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "address": "123 Main St, City, Country",
        "emergency_contact_name": "Jane Doe",
        "emergency_contact_phone": "+0987654321",
        "medical_history": "Hypertension, Type 2 Diabetes",
        "current_medications": "Lisinopril 10mg, Metformin 500mg",
        "allergies": "Penicillin"
    }
    
    response = client.post("/patients/", json=patient_data)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert data["is_active"] == True
    assert "id" in data
    
    return data["id"]

def test_get_patient():
    """Test getting patient details"""
    # First create a patient
    patient_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "date_of_birth": "1990-05-15T00:00:00",
        "gender": "female",
        "email": "jane.smith@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    patient_id = create_response.json()["id"]
    
    # Get the patient
    response = client.get(f"/patients/{patient_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == patient_id
    assert data["first_name"] == "Jane"
    assert data["email"] == "jane.smith@example.com"

def test_update_patient():
    """Test updating patient information"""
    # Create a patient first
    patient_data = {
        "first_name": "Bob",
        "last_name": "Johnson",
        "date_of_birth": "1975-08-20T00:00:00",
        "gender": "male",
        "email": "bob.johnson@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
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

def test_list_patients():
    """Test listing all patients"""
    response = client.get("/patients/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Test with pagination
    response = client.get("/patients/?skip=0&limit=2")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 2

def test_create_duplicate_patient_email():
    """Test creating patient with duplicate email"""
    patient_data = {
        "first_name": "Alice",
        "last_name": "Brown",
        "date_of_birth": "1985-03-10T00:00:00",
        "gender": "female",
        "email": "alice.brown@example.com"
    }
    
    # First creation should succeed
    response1 = client.post("/patients/", json=patient_data)
    assert response1.status_code == 201
    
    # Second creation with same email should fail
    response2 = client.post("/patients/", json=patient_data)
    assert response2.status_code == 400
    assert "already exists" in response2.json()["detail"]

def test_get_nonexistent_patient():
    """Test getting a patient that doesn't exist"""
    response = client.get("/patients/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_patient_measurements():
    """Test getting patient measurements"""
    # First create a patient
    patient_data = {
        "first_name": "Test",
        "last_name": "Patient",
        "date_of_birth": "1990-01-01T00:00:00",
        "gender": "male",
        "email": "test.patient@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    patient_id = create_response.json()["id"]
    
    # Get measurements (should be empty initially)
    response = client.get(f"/patients/{patient_id}/measurements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_patient_alerts():
    """Test getting patient alerts"""
    # Create a patient
    patient_data = {
        "first_name": "Alert",
        "last_name": "Test",
        "date_of_birth": "1990-01-01T00:00:00",
        "gender": "male",
        "email": "alert.test@example.com"
    }
    
    create_response = client.post("/patients/", json=patient_data)
    patient_id = create_response.json()["id"]
    
    # Get alerts (should be empty initially)
    response = client.get(f"/patients/{patient_id}/alerts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_patient_stats():
    """Test getting patient statistics"""
    response = client.get("/patients/stats/overall")
    assert response.status_code == 200
    data = response.json()
    assert "total_patients" in data
    assert "active_patients" in data
    assert isinstance(data["total_patients"], int)