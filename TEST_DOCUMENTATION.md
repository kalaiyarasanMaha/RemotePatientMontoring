# Test Suite Documentation

## Overview
Comprehensive test suite for Patient Monitoring Platform API with proper fixtures and database isolation.

## Test Files

### 1. test_mesaurement.py - Measurement Tests (6 tests)
- **TC-MEA-001**: Create single measurement
  - Verifies measurement created with correct values
  - Validates device_id returns string identifier
  
- **TC-MEA-002**: Measurement validation
  - Tests invalid device, invalid blood oxygen > 100%, non-existent patient
  
- **TC-MEA-003**: Batch measurement creation
  - Creates 3 measurements in single batch request
  - Validates all measurements created successfully
  
- **TC-MEA-004**: List measurements with filtering
  - Tests listing by patient_id
  - Validates device_id returns string identifier in responses
  
- **TC-MEA-005**: Get specific measurement
  - Retrieves measurement by ID
  - Validates all fields returned correctly

### 2. test_devices.py - Device Tests (5 tests)
- **TC-DEV-001**: Register device
  - Creates device with valid data
  - Validates device_id matches request
  
- **TC-DEV-002**: Update device battery
  - Updates battery level
  - Validates update successful
  
- **TC-DEV-003**: Device sync
  - Tests device sync endpoint
  - Validates last_sync_time updated
  - Uses string identifier for sync endpoint
  
- **TC-DEV-004**: List devices
  - Lists devices for patient
  - Validates filtering by patient_id
  
- **TC-DEV-005**: Device validation
  - Tests invalid device type
  - Tests non-existent patient

### 3. test_alerts.py - Alert Tests (8 tests)
- **TC-ALT-001**: Create manual alert
  - Creates alert with alert_data
  - Validates status = "active"
  
- **TC-ALT-002**: Acknowledge alert
  - Changes status to "acknowledged"
  - Validates timestamps and notes
  
- **TC-ALT-003**: Resolve alert
  - Changes status to "resolved"
  - Validates resolution notes
  
- **TC-ALT-004**: List alerts with filtering
  - Lists alerts by patient_id
  - Validates filtering
  
- **TC-ALT-005**: Get specific alert
  - Retrieves alert by ID
  - Validates all fields
  
- **TC-ALT-006**: Create alert rule
  - Creates rule with condition dict
  - Validates condition properly stored/retrieved
  
- **TC-ALT-007**: List alert rules
  - Lists active rules
  - Filters by is_active=true
  
- **TC-ALT-008**: Get specific alert rule
  - Retrieves rule by ID
  - Validates condition is dict (not JSON string in response)

### 4. test_patients.py - Patient Tests (already complete)
- Tests patient creation and validation

## Key Features

### Fixtures
- `setup_database`: Module-scoped database setup
- `test_patient`: Creates test patient
- `test_device`: Creates test device
- `test_alert_rule`: Creates test alert rule
- `client`: TestClient with overridden database

### Database
- Each test file uses separate SQLite database (test_mesaurement.db, test_devices.db, etc.)
- Tables created and dropped per session
- Clean isolation between test files

### Response Validation
All tests validate that `device_id` in responses returns:
- **String identifier** (e.g., "TEST-DEVICE-001") ✅
- NOT database ID (e.g., 7) ❌

## Running Tests

### Run all tests:
```bash
pytest -v
```

### Run specific test file:
```bash
pytest -v tests/test_mesaurement.py
```

### Run specific test:
```bash
pytest -v tests/test_mesaurement.py::test_measurement_creation
```

### Run with coverage:
```bash
pytest --cov=app tests/
```

## Test Dependencies

Required in `requirements.txt`:
- pytest
- pytest-cov
- httpx
- SQLAlchemy
- FastAPI
- pydantic

## Notes

- All endpoints tested with proper error handling
- Device IDs resolved correctly (int or string)
- JSON serialization tested (alert_data, condition fields)
- Enum values properly handled in responses
- Timestamps and created_at/updated_at fields validated
