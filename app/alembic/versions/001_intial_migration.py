"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create patients table
    op.create_table('patients',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=False),
        sa.Column('date_of_birth', sa.DateTime(), nullable=False),
        sa.Column('gender', sa.String(length=10), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('emergency_contact_name', sa.String(length=100), nullable=True),
        sa.Column('emergency_contact_phone', sa.String(length=20), nullable=True),
        sa.Column('medical_history', sa.Text(), nullable=True),
        sa.Column('current_medications', sa.Text(), nullable=True),
        sa.Column('allergies', sa.Text(), nullable=True),
        sa.Column('primary_physician_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_patients_id'), 'patients', ['id'], unique=False)
    
    # Create devices table
    op.create_table('devices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.String(length=100), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('device_type', sa.Enum('SMARTWATCH', 'BLOOD_PRESSURE_MONITOR', 'GLUCOSE_METER', 'PULSE_OXIMETER', 'ECG_MONITOR', 'TEMPERATURE_SENSOR', 'ACTIVITY_TRACKER', name='devicetype'), nullable=False),
        sa.Column('manufacturer', sa.String(length=100), nullable=True),
        sa.Column('model', sa.String(length=100), nullable=True),
        sa.Column('serial_number', sa.String(length=100), nullable=True),
        sa.Column('firmware_version', sa.String(length=50), nullable=True),
        sa.Column('last_sync_time', sa.DateTime(timezone=True), nullable=True),
        sa.Column('battery_level', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'MAINTENANCE', 'RETIRED', name='devicestatus'), nullable=True),
        sa.Column('calibration_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('calibration_due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('device_id'),
        sa.UniqueConstraint('serial_number')
    )
    op.create_index(op.f('ix_devices_id'), 'devices', ['id'], unique=False)
    
    # Create measurements table
    op.create_table('measurements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('device_id', sa.Integer(), nullable=False),
        sa.Column('heart_rate', sa.Float(), nullable=True),
        sa.Column('systolic_bp', sa.Float(), nullable=True),
        sa.Column('diastolic_bp', sa.Float(), nullable=True),
        sa.Column('blood_oxygen', sa.Float(), nullable=True),
        sa.Column('temperature', sa.Float(), nullable=True),
        sa.Column('respiratory_rate', sa.Float(), nullable=True),
        sa.Column('blood_glucose', sa.Float(), nullable=True),
        sa.Column('weight', sa.Float(), nullable=True),
        sa.Column('height', sa.Float(), nullable=True),
        sa.Column('bmi', sa.Float(), nullable=True),
        sa.Column('steps', sa.Integer(), nullable=True),
        sa.Column('calories_burned', sa.Float(), nullable=True),
        sa.Column('distance', sa.Float(), nullable=True),
        sa.Column('active_minutes', sa.Integer(), nullable=True),
        sa.Column('ecg_data', sa.Text(), nullable=True),
        sa.Column('ecg_analysis', sa.Text(), nullable=True),
        sa.Column('measurement_time', sa.DateTime(timezone=True), nullable=False),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('accuracy', sa.Float(), nullable=True),
        sa.Column('data_source', sa.String(length=50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['device_id'], ['devices.id'], ),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_measurements_id'), 'measurements', ['id'], unique=False)
    
    # Create alerts table
    op.create_table('alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('patient_id', sa.Integer(), nullable=False),
        sa.Column('alert_type', sa.Enum('HEART_RATE_HIGH', 'HEART_RATE_LOW', 'BLOOD_PRESSURE_HIGH', 'BLOOD_OXYGEN_LOW', 'TEMPERATURE_HIGH', 'GLUCOSE_HIGH', 'GLUCOSE_LOW', 'FALL_DETECTED', 'DEVICE_OFFLINE', 'MEDICATION_REMINDER', 'APPOINTMENT_REMINDER', name='alerttype'), nullable=False),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alertseverity'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('alert_data', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'DISMISSED', name='alertstatus'), nullable=True),
        sa.Column('acknowledged_by', sa.Integer(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('acknowledgment_notes', sa.Text(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('triggered_by_measurement_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ),
        sa.ForeignKeyConstraint(['triggered_by_measurement_id'], ['measurements.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    
    # Create alert_rules table
    op.create_table('alert_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('alert_type', sa.Enum('HEART_RATE_HIGH', 'HEART_RATE_LOW', 'BLOOD_PRESSURE_HIGH', 'BLOOD_OXYGEN_LOW', 'TEMPERATURE_HIGH', 'GLUCOSE_HIGH', 'GLUCOSE_LOW', 'FALL_DETECTED', 'DEVICE_OFFLINE', 'MEDICATION_REMINDER', 'APPOINTMENT_REMINDER', name='alerttype'), nullable=False),
        sa.Column('condition', sa.Text(), nullable=True),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='alertseverity'), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alert_rules_id'), 'alert_rules', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_alert_rules_id'), table_name='alert_rules')
    op.drop_table('alert_rules')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_measurements_id'), table_name='measurements')
    op.drop_table('measurements')
    op.drop_index(op.f('ix_devices_id'), table_name='devices')
    op.drop_table('devices')
    op.drop_index(op.f('ix_patients_id'), table_name='patients')
    op.drop_table('patients')
    op.execute('DROP TYPE devicetype')
    op.execute('DROP TYPE devicestatus')
    op.execute('DROP TYPE alerttype')
    op.execute('DROP TYPE alertseverity')
    op.execute('DROP TYPE alertstatus')