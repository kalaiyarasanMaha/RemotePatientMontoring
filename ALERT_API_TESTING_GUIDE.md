# Alert API Testing Guide

## Overview
This guide covers all alert-related endpoints in the Patient Monitoring Platform with sample data and curl examples.

---

## Prerequisites

### 1. Start the API Server
```bash
cd /Users/kalaiyarasanmahalingam/Desktop/project/patient_monitoring_platform
uvicorn app.main:app --reload --port 8000
```

### 2. Install Python Requests (for automated testing)
```bash
pip install requests
```

### 3. Ensure Test Data Exists
- Patient ID: 3 (use existing or create new)
- Device: "SMARTWATCH-001" or "BPM-0456"
- Measurement: Create one with elevated heart rate

---

## Quick Test: Run Automated Test Suite

```bash
python3 test_alerts_api.py
```

This will:
- ✅ Create test patient, device, and measurement
- ✅ Test all alert operations (create, list, get, acknowledge, resolve)
- ✅ Test alert rules (create, list)
- ✅ Test measurement alert detection
- ✅ Get statistics and active alert counts

---

## Manual Testing with CURL

### 1️⃣ CREATE ALERT

**Endpoint:** `POST /alerts/`

**Request:**
```bash
curl -X POST 'http://127.0.0.1:8000/alerts/' \
  -H 'Content-Type: application/json' \
  -d '{
    "patient_id": 3,
    "alert_type": "heart_rate_high",
    "severity": "high",
    "title": "Elevated Heart Rate Alert",
    "description": "Patient heart rate sustained above normal range",
    "alert_data": {
      "current_heart_rate": 125,
      "normal_range_max": 100,
      "duration_minutes": 10,
      "recommended_action": "Monitor vital signs"
    },
    "triggered_by_measurement_id": 1
  }'
```

**Expected Response (201 Created):**
```json
{
  "id": 1,
  "patient_id": 3,
  "alert_type": "heart_rate_high",
  "severity": "high",
  "title": "Elevated Heart Rate Alert",
  "description": "Patient heart rate sustained above normal range",
  "alert_data": {
    "current_heart_rate": 125,
    "normal_range_max": 100,
    "duration_minutes": 10,
    "recommended_action": "Monitor vital signs"
  },
  "status": "active",
  "acknowledged_by": null,
  "acknowledged_at": null,
  "acknowledgment_notes": null,
  "resolved_by": null,
  "resolved_at": null,
  "resolution_notes": null,
  "triggered_by_measurement_id": 1,
  "created_at": "2025-12-15T10:30:00Z",
  "updated_at": null
}
```

---

### 2️⃣ LIST ALL ALERTS

**Endpoint:** `GET /alerts/`

**Request:**
```bash
curl -X GET 'http://127.0.0.1:8000/alerts/' \
  -H 'Content-Type: application/json'
```

**With Filters:**
```bash
# Filter by patient
curl -X GET 'http://127.0.0.1:8000/alerts/?patient_id=3' \
  -H 'Content-Type: application/json'

# Filter by status
curl -X GET 'http://127.0.0.1:8000/alerts/?status=active' \
  -H 'Content-Type: application/json'

# Filter by severity
curl -X GET 'http://127.0.0.1:8000/alerts/?severity=high' \
  -H 'Content-Type: application/json'

# Filter by type
curl -X GET 'http://127.0.0.1:8000/alerts/?alert_type=heart_rate_high' \
  -H 'Content-Type: application/json'

# Include resolved alerts
curl -X GET 'http://127.0.0.1:8000/alerts/?include_resolved=true' \
  -H 'Content-Type: application/json'

# Pagination
curl -X GET 'http://127.0.0.1:8000/alerts/?skip=0&limit=50' \
  -H 'Content-Type: application/json'
```

---

### 3️⃣ GET ALERT BY ID

**Endpoint:** `GET /alerts/{alert_id}`

**Request:**
```bash
curl -X GET 'http://127.0.0.1:8000/alerts/1' \
  -H 'Content-Type: application/json'
```

---

### 4️⃣ ACKNOWLEDGE ALERT

**Endpoint:** `POST /alerts/{alert_id}/acknowledge`

**Request:**
```bash
curl -X POST 'http://127.0.0.1:8000/alerts/1/acknowledge' \
  -H 'Content-Type: application/json' \
  -d '{
    "acknowledgment_notes": "Alert reviewed. Patient is stable. Will continue monitoring."
  }'
```

**Response:**
```json
{
  "id": 1,
  "status": "acknowledged",
  "acknowledged_by": 1,
  "acknowledged_at": "2025-12-15T10:35:00Z",
  "acknowledgment_notes": "Alert reviewed. Patient is stable. Will continue monitoring.",
  ...
}
```

---

### 5️⃣ RESOLVE ALERT

**Endpoint:** `POST /alerts/{alert_id}/resolve`

**Request:**
```bash
curl -X POST 'http://127.0.0.1:8000/alerts/1/resolve' \
  -H 'Content-Type: application/json' \
  -d '{
    "resolution_notes": "Heart rate returned to normal. Alert can be closed."
  }'
```

**Response:**
```json
{
  "id": 1,
  "status": "resolved",
  "resolved_by": 1,
  "resolved_at": "2025-12-15T10:40:00Z",
  "resolution_notes": "Heart rate returned to normal. Alert can be closed.",
  ...
}
```

---

### 6️⃣ UPDATE ALERT

**Endpoint:** `PUT /alerts/{alert_id}`

**Request:**
```bash
curl -X PUT 'http://127.0.0.1:8000/alerts/1' \
  -H 'Content-Type: application/json' \
  -d '{
    "status": "acknowledged"
  }'
```

---

### 7️⃣ CREATE ALERT RULE

**Endpoint:** `POST /alerts/rules/`

**Request:**
```bash
curl -X POST 'http://127.0.0.1:8000/alerts/rules/' \
  -H 'Content-Type: application/json' \
  -d '{
    "name": "High Heart Rate Detection",
    "alert_type": "heart_rate_high",
    "condition": {
      "parameter": "heart_rate",
      "operator": "greater_than",
      "threshold": 100,
      "duration_minutes": 5
    },
    "severity": "high",
    "is_active": true
  }'
```

---

### 8️⃣ LIST ALERT RULES

**Endpoint:** `GET /alerts/rules/`

**Request:**
```bash
curl -X GET 'http://127.0.0.1:8000/alerts/rules/' \
  -H 'Content-Type: application/json'

# Filter by active status
curl -X GET 'http://127.0.0.1:8000/alerts/rules/?is_active=true' \
  -H 'Content-Type: application/json'
```

---

### 9️⃣ GET ALERT RULE BY ID

**Endpoint:** `GET /alerts/rules/{rule_id}`

**Request:**
```bash
curl -X GET 'http://127.0.0.1:8000/alerts/rules/1' \
  -H 'Content-Type: application/json'
```

---

### 🔟 UPDATE ALERT RULE

**Endpoint:** `PUT /alerts/rules/{rule_id}`

**Request:**
```bash
curl -X PUT 'http://127.0.0.1:8000/alerts/rules/1' \
  -H 'Content-Type: application/json' \
  -d '{
    "is_active": false
  }'
```

---

### 1️⃣1️⃣ DELETE ALERT RULE

**Endpoint:** `DELETE /alerts/rules/{rule_id}`

**Request:**
```bash
curl -X DELETE 'http://127.0.0.1:8000/alerts/rules/1' \
  -H 'Content-Type: application/json'
```

---

### 1️⃣2️⃣ TEST MEASUREMENT FOR ALERTS

**Endpoint:** `POST /alerts/test/measurement/{measurement_id}`

This endpoint analyzes a measurement and returns any alerts that would be triggered.

**Request:**
```bash
curl -X POST 'http://127.0.0.1:8000/alerts/test/measurement/1' \
  -H 'Content-Type: application/json'
```

**Response Example:**
```json
{
  "measurement_id": 1,
  "alerts_detected": 2,
  "alerts": [
    {
      "id": 2,
      "alert_type": "heart_rate_high",
      "severity": "high",
      ...
    },
    {
      "id": 3,
      "alert_type": "blood_pressure_high",
      "severity": "medium",
      ...
    }
  ]
}
```

---

### 1️⃣3️⃣ GET ACTIVE ALERTS COUNT

**Endpoint:** `GET /alerts/active/count`

**Request:**
```bash
# All active alerts
curl -X GET 'http://127.0.0.1:8000/alerts/active/count' \
  -H 'Content-Type: application/json'

# For specific patient
curl -X GET 'http://127.0.0.1:8000/alerts/active/count?patient_id=3' \
  -H 'Content-Type: application/json'
```

**Response:**
```json
{
  "active_alerts_count": 5
}
```

---

### 1️⃣4️⃣ GET ALERT STATISTICS

**Endpoint:** `GET /alerts/stats/overall`

**Request:**
```bash
# Last 7 days (default)
curl -X GET 'http://127.0.0.1:8000/alerts/stats/overall' \
  -H 'Content-Type: application/json'

# Last 30 days
curl -X GET 'http://127.0.0.1:8000/alerts/stats/overall?days=30' \
  -H 'Content-Type: application/json'
```

**Response Example:**
```json
{
  "total_alerts": 25,
  "active_alerts": 3,
  "acknowledged_alerts": 10,
  "resolved_alerts": 12,
  "high_severity_count": 5,
  "critical_severity_count": 2,
  "alerts_by_type": {
    "heart_rate_high": 8,
    "blood_pressure_high": 6,
    "temperature_high": 4,
    ...
  }
}
```

---

## Alert Types

```
- heart_rate_high
- heart_rate_low
- blood_pressure_high
- blood_oxygen_low
- temperature_high
- glucose_high
- glucose_low
- fall_detected
- device_offline
- medication_reminder
- appointment_reminder
```

## Alert Severity Levels

```
- low
- medium
- high
- critical
```

## Alert Status Values

```
- active       (Initial state)
- acknowledged (Reviewed by clinician)
- resolved     (Issue resolved)
- dismissed    (Dismissed without action)
```

---

## Complete Workflow Example

```bash
# 1. Create an alert
ALERT_ID=$(curl -s -X POST 'http://127.0.0.1:8000/alerts/' \
  -H 'Content-Type: application/json' \
  -d '{
    "patient_id": 3,
    "alert_type": "heart_rate_high",
    "severity": "high",
    "title": "High Heart Rate",
    "description": "Patient heart rate is elevated"
  }' | jq '.id')

echo "Created Alert ID: $ALERT_ID"

# 2. View the alert
curl -X GET "http://127.0.0.1:8000/alerts/$ALERT_ID"

# 3. Acknowledge the alert
curl -X POST "http://127.0.0.1:8000/alerts/$ALERT_ID/acknowledge" \
  -H 'Content-Type: application/json' \
  -d '{"acknowledgment_notes": "Reviewed by doctor"}'

# 4. Resolve the alert
curl -X POST "http://127.0.0.1:8000/alerts/$ALERT_ID/resolve" \
  -H 'Content-Type: application/json' \
  -d '{"resolution_notes": "Patient is stable now"}'

# 5. View resolved alert
curl -X GET "http://127.0.0.1:8000/alerts/$ALERT_ID"
```

---

## Troubleshooting

### Error: "Patient with ID X not found"
- Ensure patient exists: `GET /patients/3`
- Create a patient first if needed: `POST /patients/`

### Error: "Cannot acknowledge a resolved alert"
- Cannot acknowledge an already resolved alert
- Resolve or dismiss the alert instead

### Error: "Alert is already resolved"
- The alert has already been resolved
- Cannot resolve an alert twice

### Alerts not being detected from measurement
- Check the measurement values are extreme enough to trigger alerts
- Review alert rules to ensure they're active
- Use `POST /alerts/test/measurement/{id}` to debug

---

## Performance Tips

1. Use pagination when listing alerts:
   ```bash
   curl 'http://127.0.0.1:8000/alerts/?skip=0&limit=50'
   ```

2. Filter by status to reduce results:
   ```bash
   curl 'http://127.0.0.1:8000/alerts/?status=active'
   ```

3. Use date filters:
   ```bash
   curl 'http://127.0.0.1:8000/alerts/?start_date=2025-12-01&end_date=2025-12-15'
   ```

4. Only include resolved when needed:
   ```bash
   curl 'http://127.0.0.1:8000/alerts/?include_resolved=false'
   ```

---

## Support

For issues or questions:
1. Check API logs: `tail -f /path/to/logs`
2. Run automated tests: `python3 test_alerts_api.py`
3. Verify database connection
4. Check patient/device/measurement IDs exist
