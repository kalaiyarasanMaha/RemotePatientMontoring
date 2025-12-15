# Remote Patient Monitoring Platform

A comprehensive platform for monitoring patient biometric data from wearable devices, analyzing trends, and providing alerts to clinicians.

## Features

### Patients Management
- Create and manage patient profiles
- View patient details and medical history
- Track patient devices and measurements

### Device Management
- Register and assign wearable devices to patients
- Monitor device status and battery levels
- Track device synchronization

### Measurements Collection
- Record various biometric measurements (heart rate, blood pressure, oxygen levels, etc.)
- Support for batch measurements upload
- Automatic BMI calculation

### Alerts System
- Real-time alert generation based on measurement thresholds
- Configurable alert rules
- Alert acknowledgment and resolution tracking
- Trend-based anomaly detection

### Analytics
- Patient vitals summary and trends
- Health risk assessment
- Statistical analysis of measurements
- Anomaly detection

## API Endpoints

### Patients
- `POST /patients` - Create patient (clinician/admin)
- `GET /patients/{id}` - Patient details
- `GET /patients/{id}/measurements` - List measurements
- `GET /patients/{id}/alerts` - List alerts

### Devices
- `POST /devices` - Register device (assign to patient)
- `GET /devices/{id}` - Device details

### Alerts
- `GET /alerts` - List alerts (filterable)
- `POST /alerts/{id}/ack` - Acknowledge alert
- `POST /alert-rules` - Create alert rule (admin)

### Measurements
- `POST /measurements` - Create measurement
- `GET /measurements` - List measurements
- `POST /measurements/batch` - Batch create measurements

## Tech Stack

- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Task Queue**: Celery with Redis
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest
- **Database Migrations**: Alembic

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd patient-monitoring-platform   