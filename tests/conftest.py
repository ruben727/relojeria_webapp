import pytest
from fastapi.testclient import TestClient
from app.main import app, init_db

@pytest.fixture(scope="session", autouse=True)
def setup_database():
    """Initialize database before all tests"""
    init_db()
    yield

@pytest.fixture
def client():
    return TestClient(app)
