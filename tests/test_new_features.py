import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
import copy

from tests.test_features import mock_db, fastapi_app, get_current_user, admin_only, MOCK_USER_ID, MOCK_ADMIN_ID, MockCollection

# Dynamically add the new collections to mock_db if not exists
if not hasattr(mock_db, "otps"):
    mock_db.otps = MockCollection("otps")
if not hasattr(mock_db, "notifications"):
    mock_db.notifications = MockCollection("notifications")
if not hasattr(mock_db, "admins"):
    mock_db.admins = MockCollection("admins")

# Patch router and service DB attributes to point to mock_db
import app.routers.auth
import app.routers.notifications
import app.routers.users
import app.routers.admin_dashboard
import app.services.otp
import app.services.user
import app.services.auth

client = TestClient(fastapi_app)

# Define overrides matching those in test_features but local to this file
async def override_get_current_user():
    return {
        "id": MOCK_USER_ID,
        "userId": MOCK_USER_ID,
        "email": "jane@example.com",
        "role": "PATIENT",
        "fullName": "Jane User"
    }

async def override_admin_only():
    return {
        "id": MOCK_ADMIN_ID,
        "userId": MOCK_ADMIN_ID,
        "email": "admin@docton.com",
        "role": "ADMIN",
        "fullName": "Test Admin"
    }

@pytest.fixture(autouse=True)
def setup_test_overrides():
    # Patch all db properties to ensure correct routing in all relevant modules
    app.database.db = mock_db
    app.services.auth.db = mock_db
    app.services.otp.db = mock_db
    app.services.user.db = mock_db
    app.routers.auth.db = mock_db
    app.routers.notifications.db = mock_db
    app.routers.users.db = mock_db
    app.routers.admin_dashboard.db = mock_db

    # Apply dependency overrides
    from app.middlewares.auth import get_current_user, admin_only
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    fastapi_app.dependency_overrides[admin_only] = override_admin_only
    
    # Custom $or patch for users find_one
    original_find_one = mock_db.users.find_one
    async def find_one_patched(query):
        if "$or" in query:
            for doc in mock_db.users.docs:
                for item in query["$or"]:
                    match = True
                    for k, v in item.items():
                        if doc.get(k) != v:
                            match = False
                            break
                    if match:
                        return copy.deepcopy(doc)
            return None
        return await original_find_one(query)
    mock_db.users.find_one = find_one_patched
    
    # Deepcopy insert_one for notifications to prevent reference mutation side-effects
    original_insert_one = mock_db.notifications.insert_one
    async def insert_one_patched(doc):
        doc_copy = copy.deepcopy(doc)
        return await original_insert_one(doc_copy)
    mock_db.notifications.insert_one = insert_one_patched

    # Custom $or and $in patch for notifications find
    original_find = mock_db.notifications.find
    def find_patched(query=None, projection=None):
        if query and "$or" in query:
            filtered = []
            for doc in mock_db.notifications.docs:
                match_any = False
                for clause in query["$or"]:
                    clause_match = True
                    for k, v in clause.items():
                        doc_val = doc.get(k)
                        if isinstance(v, dict) and "$in" in v:
                            if doc_val not in v["$in"]:
                                clause_match = False
                                break
                        elif doc_val != v:
                            clause_match = False
                            break
                    if clause_match:
                        match_any = True
                        break
                if match_any:
                    filtered.append(doc)
            
            class MockCursor:
                def __init__(self, items):
                    self.items = items
                def sort(self, *args, **kwargs):
                    return self
                def limit(self, *args, **kwargs):
                    return self
                def skip(self, *args, **kwargs):
                    return self
                async def to_list(self, length=None):
                    res = [copy.deepcopy(d) for d in self.items]
                    if length is not None:
                        res = res[:length]
                    return res
            return MockCursor(filtered)
            
        return original_find(query, projection)
    mock_db.notifications.find = find_patched
    
    # Patch update_one to support $addToSet in notifications mock
    async def update_one_patched(query, update):
        for doc in mock_db.notifications.docs:
            if doc.get("_id") == query.get("_id"):
                if "$set" in update:
                    for uk, uv in update["$set"].items():
                        doc[uk] = uv
                if "$addToSet" in update:
                    for uk, uv in update["$addToSet"].items():
                        if uk not in doc or not isinstance(doc[uk], list):
                            doc[uk] = []
                        if uv not in doc[uk]:
                            doc[uk].append(uv)
                return MagicMock(modified_count=1)
        return MagicMock(modified_count=0)
    mock_db.notifications.update_one = update_one_patched

    # Patch update_many in notifications mock
    async def update_many_patched(query, update):
        modified_count = 0
        for doc in mock_db.notifications.docs:
            match = True
            if "recipientId" in query and doc.get("recipientId") != query["recipientId"]:
                match = False
            if "recipientRole" in query:
                role_filter = query["recipientRole"]
                if isinstance(role_filter, dict) and "$in" in role_filter:
                    if doc.get("recipientRole") not in role_filter["$in"]:
                        match = False
            if "readBy" in query:
                read_filter = query["readBy"]
                if isinstance(read_filter, dict) and "$ne" in read_filter:
                    if read_filter["$ne"] in doc.get("readBy", []):
                        match = False
            
            if match:
                if "$set" in update:
                    for uk, uv in update["$set"].items():
                        doc[uk] = uv
                if "$addToSet" in update:
                    for uk, uv in update["$addToSet"].items():
                        if uk not in doc or not isinstance(doc[uk], list):
                            doc[uk] = []
                        if uv not in doc[uk]:
                            doc[uk].append(uv)
                modified_count += 1
        return MagicMock(modified_count=modified_count)
    mock_db.notifications.update_many = update_many_patched
    
    yield
    # Clean up overrides
    fastapi_app.dependency_overrides.clear()


# ==================== FORGOT PASSWORD & OTP ====================
@patch("app.routers.auth.send_email", new_callable=AsyncMock)
def test_forgot_password_and_reset_flow(mock_send_email):
    # Setup mock user in db.users
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Jane User",
        "email": "jane@example.com",
        "role": "PATIENT",
        "password": "old_hashed_password"
    }]
    mock_db.otps.docs = []
    
    # 1. Forgot password request
    forgot_payload = {
        "email": "jane@example.com",
        "role": "USER"
    }
    response = client.post("/api/auth/forgot-password", json=forgot_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert mock_send_email.called
    
    # Get the sent OTP from DB
    otp_record = mock_db.otps.docs[0]
    assert otp_record["email"] == "jane@example.com"
    sent_otp = otp_record["otp"]
    
    # 2. Reset password request
    reset_payload = {
        "email": "jane@example.com",
        "otp": sent_otp,
        "password": "new_secure_password",
        "role": "USER"
    }
    response_reset = client.post("/api/auth/reset-password", json=reset_payload)
    assert response_reset.status_code == 200
    assert response_reset.json()["success"] is True
    
    # Verify password was updated in DB
    updated_user = mock_db.users.docs[0]
    assert updated_user["password"] != "old_hashed_password"

@patch("app.routers.auth.send_email", new_callable=AsyncMock)
def test_resend_otp(mock_send_email):
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Jane User",
        "email": "jane@example.com",
        "role": "PATIENT"
    }]
    mock_db.otps.docs = []
    
    payload = {
        "email": "jane@example.com",
        "role": "USER"
    }
    response = client.post("/api/auth/resend-otp", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert mock_send_email.called


# ==================== S3 PROFILE PIC UPLOAD ====================
@patch("app.routers.users.storage_service.upload_file")
def test_profile_pic_upload(mock_upload_file):
    # Setup mock user in db.users
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Jane User",
        "email": "jane@example.com",
        "profilePic": None
    }]
    
    mock_upload_file.return_value = "https://s3.amazonaws.com/docton/profile_pics/jane.jpg"
    
    # Upload binary file
    response = client.post(
        "/api/users/profile-pic",
        files={"file": ("jane.jpg", b"dummy_image_content", "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["profilePic"] == "https://s3.amazonaws.com/docton/profile_pics/jane.jpg"
    
    # Verify updated in DB
    assert mock_db.users.docs[0]["profilePic"] == "https://s3.amazonaws.com/docton/profile_pics/jane.jpg"


# ==================== ADMIN USERS & PROVIDERS ====================
def test_admin_get_users_and_providers():
    # Setup data
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Jane Patient",
        "email": "jane@example.com",
        "profilePic": "https://s3.amazonaws.com/docton/jane.jpg",
        "isOnline": 1
    }]
    mock_db.doctors.docs = [{
        "_id": ObjectId(),
        "name": "Dr. House",
        "email": "house@example.com",
        "profileImage": "https://s3.amazonaws.com/docton/house.jpg",
        "isOnline": 1,
        "verificationStatus": 1
    }]
    mock_db.nurses.docs = [{
        "_id": ObjectId(),
        "name": "Nurse Jackie",
        "email": "jackie@example.com",
        "profileImage": "https://s3.amazonaws.com/docton/jackie.jpg",
        "isOnline": 0,
        "verificationStatus": 1
    }]
    
    # Get users
    response_users = client.get("/api/admin/users")
    assert response_users.status_code == 200
    users_data = response_users.json()
    assert users_data["success"] is True
    assert users_data["count"] == 1
    assert users_data["data"][0]["name"] == "Jane Patient"
    assert users_data["data"][0]["profilePic"] == "https://s3.amazonaws.com/docton/jane.jpg"
    
    # Get providers
    response_provs = client.get("/api/admin/providers")
    assert response_provs.status_code == 200
    provs_data = response_provs.json()
    assert provs_data["success"] is True
    assert provs_data["count"] == 2
    assert provs_data["data"][0]["name"] == "Dr. House"
    assert provs_data["data"][1]["name"] == "Nurse Jackie"
    assert provs_data["data"][0]["profilePic"] == "https://s3.amazonaws.com/docton/house.jpg"
    assert provs_data["data"][1]["profilePic"] == "https://s3.amazonaws.com/docton/jackie.jpg"


# ==================== REAL-TIME NOTIFICATIONS ====================
@patch("app.routers.notifications.socket_service", new_callable=AsyncMock)
def test_notification_flow(mock_socket):
    mock_db.notifications.docs = []
    
    # 1. Admin sends a broadcast notification
    notif_payload = {
        "recipientRole": "ALL",
        "title": "System Update",
        "body": "We are upgrading the servers tonight.",
        "type": "SYSTEM"
    }
    response_send = client.post("/api/admin/notifications/send", json=notif_payload)
    assert response_send.status_code == 200
    send_data = response_send.json()
    assert send_data["success"] is True
    assert len(mock_db.notifications.docs) == 1
    
    # 2. Get my notifications
    response_list = client.get("/api/notifications")
    assert response_list.status_code == 200
    list_data = response_list.json()
    assert list_data["success"] is True
    assert list_data["count"] == 1
    assert list_data["data"][0]["title"] == "System Update"
    assert list_data["data"][0]["isRead"] is False
    
    # 3. Mark as read
    notif_id = list_data["data"][0]["id"]
    response_read = client.patch(f"/api/notifications/{notif_id}/read")
    assert response_read.status_code == 200
    assert response_read.json()["success"] is True
    
    # 4. Get notifications again and verify it is read
    response_list2 = client.get("/api/notifications")
    assert response_list2.json()["data"][0]["isRead"] is True
