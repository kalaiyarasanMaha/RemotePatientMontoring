# test_db.py
import sqlalchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL
database_url = os.getenv('DATABASE_URL', 'postgresql://neondb_owner:npg_7ycNS3vMiGDh@ep-purple-fire-addfbs7u-pooler.c-2.us-east-1.aws.neon.tech/patient_monitoring?sslmode=require&channel_binding=require')


# Fix URL encoding if needed
if '@' in database_url.split(':')[2].split('@')[0]:
    parts = database_url.split(':')
    password = parts[2].split('@')[0]
    encoded_password = password.replace('@', '%40')
    database_url = f"{parts[0]}:{parts[1]}:{encoded_password}@{'@'.join(parts[2].split('@')[1:])}"

print(f"Connecting to: {database_url}")

try:
    # Create engine
    engine = sqlalchemy.create_engine(database_url)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ PostgreSQL version: {version}")
        
        # List databases
        result = conn.execute(text("SELECT datname FROM pg_database;"))
        databases = [row[0] for row in result.fetchall()]
        print(f"✓ Available databases: {databases}")
        
        # Check if our database exists
        if 'patient_monitoring' in databases:
            print("✓ Database 'patient_monitoring' exists")
            
            # Switch to our database
            conn.execute(text("COMMIT"))
            conn.execute(text("SET search_path TO public"))
            
            # List tables
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"✓ Tables in database: {tables}")
        else:
            print("✗ Database 'patient_monitoring' does not exist")
            
except Exception as e:
    print(f"✗ Connection failed: {e}")