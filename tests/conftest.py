# conftest.py - Shared pytest configuration
import os
import sys
from pathlib import Path

# Add parent directory to path so app modules can be imported
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# Test database configuration - use single shared test database
TEST_SQLALCHEMY_DATABASE_URL = "sqlite:///./test_db.db"

# Create engine and session factory at module level
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Setup test database - runs once for entire session"""
    Base.metadata.create_all(bind=engine)
    yield
    # Cleanup after all tests
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(autouse=True)
def cleanup_before_test():
    """Clean up database before each test"""
    # Clear all tables before each test
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            try:
                connection.execute(text(f"DELETE FROM {table.name}"))
            except:
                pass
        connection.commit()
    yield

@pytest.fixture
def client():
    """Create test client with database session and overridden dependencies"""
    # Create a new session for this test
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test client
    test_client = TestClient(app)
    
    yield test_client
    
    # Cleanup
    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()
