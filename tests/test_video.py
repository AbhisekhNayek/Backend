import pytest
import hashlib
import json
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import app
from app.utils.zego_token import generate_token04

client = TestClient(app)

def test_generate_token04_success():
    """Test valid token04 generation produces a correct format token."""
    app_id = 123456789
    user_id = "test_user_123"
    secret = "0123456789abcdef0123456789abcdef"  # 32 bytes mock secret
    effective_time = 3600
    payload = json.dumps({"room_id": "room_xyz", "privilege": {1: 1, 2: 1}, "stream_id_list": None})
    
    token_info = generate_token04(app_id, user_id, secret, effective_time, payload)
    
    assert token_info.error_code == 0
    assert token_info.token.startswith("04")
    assert len(token_info.token) > 50

def test_generate_token04_invalid_secret():
    """Test token generation with invalid secret length."""
    app_id = 123456789
    user_id = "test_user_123"
    secret = "short_secret"  # Invalid length (must be 32 bytes)
    effective_time = 3600
    payload = "{}"
    
    token_info = generate_token04(app_id, user_id, secret, effective_time, payload)
    assert token_info.error_code != 0

@patch("app.routers.video.settings.zego_callback_secret", "dummy_callback_secret_32_chars_!")
@patch("app.routers.video.db")
def test_zegocloud_webhook_valid_signature(mock_db):
    """Test webhook logic correctly accepts valid SHA-1 signature and updates DB."""
    mock_update = AsyncMock()
    mock_db.bookings.update_one = mock_update
    timestamp = "1625097600"
    nonce = "123456"
    secret = "dummy_callback_secret_32_chars_!"
    
    # Sort and hash params just like ZEGOCLOUD server does
    params = [secret, timestamp, nonce]
    params.sort()
    joined_str = "".join(params)
    valid_signature = hashlib.sha1(joined_str.encode('utf-8')).hexdigest()
    
    payload = {
        "event": "room_close",
        "room_id": "507f1f77bcf86cd799439011" # Valid objectId format
    }
    
    response = client.post(
        f"/api/video/webhook?timestamp={timestamp}&nonce={nonce}&signature={valid_signature}",
        json=payload
    )
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    mock_update.assert_called_once()

@patch("app.routers.video.settings.zego_callback_secret", "dummy_callback_secret_32_chars_!")
def test_zegocloud_webhook_invalid_signature():
    """Test webhook rejects payload if signature does not match."""
    timestamp = "1625097600"
    nonce = "123456"
    invalid_signature = "e10adc3949ba59abbe56e057f20f883e"
    
    response = client.post(
        f"/api/video/webhook?timestamp={timestamp}&nonce={nonce}&signature={invalid_signature}",
        json={"event": "room_close"}
    )
    
    assert response.status_code == 401
    assert "Invalid webhook signature" in response.json()["detail"]
