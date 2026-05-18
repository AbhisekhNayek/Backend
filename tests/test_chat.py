import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_get_current_user():
    # Mocking the dependency in FastAPI
    async def override_get_current_user():
        return {
            "id": "test_user_123",
            "name": "Test User",
            "profilePicture": "http://example.com/pic.png",
            "role": "patient"
        }
    
    from app.middlewares.auth import get_current_user
    app.dependency_overrides[get_current_user] = override_get_current_user
    yield
    app.dependency_overrides = {}

@patch("app.routers.chat.cometchat_service")
def test_get_cometchat_token_existing_user(mock_cometchat, mock_get_current_user):
    # Setup mock to return that user already exists
    mock_cometchat.get_user = AsyncMock(return_value={"uid": "test_user_123"})
    mock_cometchat.create_auth_token = AsyncMock(return_value="mock_auth_token_123")
    
    response = client.get("/api/chat/token")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["authToken"] == "mock_auth_token_123"
    mock_cometchat.create_user.assert_not_called()

@patch("app.routers.chat.cometchat_service")
def test_get_cometchat_token_new_user(mock_cometchat, mock_get_current_user):
    # Setup mock to return that user does NOT exist
    mock_cometchat.get_user = AsyncMock(return_value=None)
    mock_cometchat.create_user = AsyncMock(return_value={"uid": "test_user_123"})
    mock_cometchat.create_auth_token = AsyncMock(return_value="mock_auth_token_123")
    
    response = client.get("/api/chat/token")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["authToken"] == "mock_auth_token_123"
    mock_cometchat.create_user.assert_called_once_with("test_user_123", "Test User", "http://example.com/pic.png")
