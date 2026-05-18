import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "Docton Backend is online" in data["message"]
    assert data["framework"] == "FastAPI (Python)"

def test_read_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "Docton Python Backend"
    assert "timestamp" in data

def test_custom_404():
    response = client.get("/api/non-existent-route-for-testing")
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert data["message"] == "Route not found"
