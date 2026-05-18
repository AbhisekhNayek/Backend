import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
import copy
import bcrypt

# ==================== HIGH-FIDELITY MOCK LAYER ====================

class MockCollection:
    def __init__(self, name):
        self.name = name
        self.docs = []

    def _get_nested(self, doc, key):
        if "." in key:
            parts = key.split(".")
            temp = doc
            for p in parts:
                if isinstance(temp, dict):
                    temp = temp.get(p)
                else:
                    return None
            return temp
        return doc.get(key)

    async def find_one(self, query, projection=None):
        for doc in self.docs:
            match = True
            if "$or" in query:
                or_match = False
                for subquery in query["$or"]:
                    sub_match = True
                    for sk, sv in subquery.items():
                        sval = self._get_nested(doc, sk)
                        if isinstance(sv, dict) and "$regex" in sv:
                            import re
                            pattern = sv["$regex"]
                            flags = re.IGNORECASE if "i" in sv.get("$options", "") else 0
                            if not re.search(pattern, str(sval or ""), flags):
                                sub_match = False
                                break
                        elif isinstance(sval, ObjectId) and isinstance(sv, str):
                            if str(sval) != sv:
                                sub_match = False
                                break
                        elif isinstance(sval, str) and isinstance(sv, ObjectId):
                            if sval != str(sv):
                                sub_match = False
                                break
                        elif sval != sv:
                            sub_match = False
                            break
                    if sub_match:
                        or_match = True
                        break
                if not or_match:
                    match = False
            for k, v in query.items():
                if k == "$or":
                    continue
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if isinstance(v, dict):
                    if "$ne" in v and doc_val == v["$ne"]:
                        match = False
                        break
                    if "$regex" in v:
                        import re
                        pattern = v["$regex"]
                        flags = re.IGNORECASE if "i" in v.get("$options", "") else 0
                        if not re.search(pattern, str(doc_val or ""), flags):
                            match = False
                            break
                elif doc_val != v:
                    match = False
                    break
            if match:
                return copy.deepcopy(doc)
        return None

    def find(self, query=None, projection=None):
        filtered = []
        for doc in self.docs:
            if not query:
                filtered.append(doc)
                continue
            match = True
            if "$or" in query:
                or_match = False
                for subquery in query["$or"]:
                    sub_match = True
                    for sk, sv in subquery.items():
                        sval = self._get_nested(doc, sk)
                        if isinstance(sv, dict) and "$regex" in sv:
                            import re
                            pattern = sv["$regex"]
                            flags = re.IGNORECASE if "i" in sv.get("$options", "") else 0
                            if not re.search(pattern, str(sval or ""), flags):
                                sub_match = False
                                break
                        elif isinstance(sval, ObjectId) and isinstance(sv, str):
                            if str(sval) != sv:
                                sub_match = False
                                break
                        elif isinstance(sval, str) and isinstance(sv, ObjectId):
                            if sval != str(sv):
                                sub_match = False
                                break
                        elif sval != sv:
                            sub_match = False
                            break
                    if sub_match:
                        or_match = True
                        break
                if not or_match:
                    match = False
            for k, v in query.items():
                if k == "$or":
                    continue
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if isinstance(v, dict):
                    if "$ne" in v and doc_val == v["$ne"]:
                        match = False
                        break
                    if "$regex" in v:
                        import re
                        pattern = v["$regex"]
                        flags = re.IGNORECASE if "i" in v.get("$options", "") else 0
                        if not re.search(pattern, str(doc_val or ""), flags):
                            match = False
                            break
                    if "$lte" in v and doc_val > v["$lte"]:
                        match = False
                        break
                    if "$gt" in v and doc_val <= v["$gt"]:
                        match = False
                        break
                else:
                    if doc_val != v:
                        match = False
                        break
            if match:
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

    def aggregate(self, pipeline):
        # Custom mock outputs for aggregates to support Analytics, Tasks, and Financials
        items = []
        if self.name == "payments":
            items = [{
                "_id": "2026-05-18",
                "totalRevenue": 1500.0,
                "platformFees": 10.0,
                "count": 10
            }]
        elif self.name in ["users", "doctors"]:
            items = [{"_id": "2026-05", "count": 5}]
        elif self.name == "bookings":
            items = [{
                "_id": ObjectId(),
                "status": "COMPLETED",
                "userId": ObjectId(),
                "user": {
                    "location": {"latitude": 12.9716, "longitude": 77.5946}
                }
            }]
        elif self.name == "booking_tasks":
            items = [{
                "_id": ObjectId(),
                "bookingId": ObjectId(),
                "title": "Vital Monitoring",
                "isCompleted": False,
                "created_at": datetime.now(timezone.utc),
                "booking": {
                    "_id": ObjectId(),
                    "userId": ObjectId(),
                    "providerId": ObjectId(),
                    "status": "ACCEPTED",
                    "bookingDate": datetime.now(timezone.utc),
                    "created_at": datetime.now(timezone.utc)
                }
            }]

        class MockCursor:
            def __init__(self, items):
                self.items = items
            async def to_list(self, length=None):
                res = [copy.deepcopy(d) for d in self.items]
                if length is not None:
                    res = res[:length]
                return res

        return MockCursor(items)

    async def insert_one(self, doc):
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.docs.append(doc)
        res = MagicMock()
        res.inserted_id = doc["_id"]
        return res

    async def update_one(self, query, update):
        modified = 0
        for doc in self.docs:
            match = True
            for k, v in query.items():
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if doc_val != v:
                    match = False
                    break
            if match:
                if "$set" in update:
                    for uk, uv in update["$set"].items():
                        doc[uk] = uv
                    modified = 1
                    break
        return MagicMock(modified_count=modified)

    async def find_one_and_update(self, query, update, projection=None, return_document=True, upsert=False, **kwargs):
        for doc in self.docs:
            match = True
            for k, v in query.items():
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if doc_val != v:
                    match = False
                    break
            if match:
                if "$set" in update:
                    for uk, uv in update["$set"].items():
                        doc[uk] = uv
                return copy.deepcopy(doc)
        if upsert:
            new_doc = copy.deepcopy(query)
            if "$set" in update:
                for uk, uv in update["$set"].items():
                    new_doc[uk] = uv
            if "_id" not in new_doc:
                new_doc["_id"] = ObjectId()
            self.docs.append(new_doc)
            return copy.deepcopy(new_doc)
        return None

    async def delete_one(self, query):
        for doc in self.docs:
            match = True
            for k, v in query.items():
                doc_val = self._get_nested(doc, k)
                if doc_val != v:
                    match = False
                    break
            if match:
                self.docs.remove(doc)
                return MagicMock(deleted_count=1)
        return MagicMock(deleted_count=0)


class MockDatabase:
    def __init__(self):
        self.users = MockCollection("users")
        self.otps = MockCollection("otps")
        self.nurses = MockCollection("nurses")
        self.doctors = MockCollection("doctors")
        self.admins = MockCollection("admins")
        self.payments = MockCollection("payments")
        self.withdrawals = MockCollection("withdrawals")
        self.bookings = MockCollection("bookings")
        self.booking_tasks = MockCollection("booking_tasks")
        self.provider_verifications = MockCollection("provider_verifications")
        self.prescriptions = MockCollection("prescriptions")
        self.visit_reports = MockCollection("visit_reports")
        self.banners = MockCollection("banners")
        self.announcements = MockCollection("announcements")
        self.system_configs = MockCollection("system_configs")
        self.activity_logs = MockCollection("activity_logs")


# Instantiate global mock database
mock_db = MockDatabase()

# Apply DB patches to all routers and services
import app.database
app.database.db = mock_db
app.database.client = MagicMock()
app.database.client.admin.command = AsyncMock(return_value={"ok": 1.0})

import app.services.user
import app.services.doctor
import app.services.billing
import app.services.tracking
import app.services.auth
import app.routers.analytics
import app.routers.auth
import app.routers.clinical
import app.routers.doctors
import app.routers.financial
import app.routers.nurses
import app.routers.system
import app.routers.tasks
import app.routers.users
import app.routers.verification

app.services.user.db = mock_db
app.services.doctor.db = mock_db
app.services.billing.db = mock_db
app.services.tracking.db = mock_db
app.services.auth.db = mock_db
app.routers.analytics.db = mock_db
app.routers.auth.db = mock_db
app.routers.clinical.db = mock_db
app.routers.doctors.db = mock_db
app.routers.financial.db = mock_db
app.routers.nurses.db = mock_db
app.routers.system.db = mock_db
app.routers.tasks.db = mock_db
app.routers.users.db = mock_db
app.routers.verification.db = mock_db

# Patch background processes and integration services
app.services.user.send_email = AsyncMock(return_value=True)
app.services.user.save_otp = AsyncMock(return_value=True)
app.routers.verification.storage_service.upload_file = MagicMock(return_value="https://docton-s3.s3.amazonaws.com/test.pdf")

# Set up FastAPI client
from app.main import app as fastapi_app
from app.middlewares.auth import get_current_user, admin_only, role_required

client = TestClient(fastapi_app)

MOCK_USER_ID = "6648cb92bc0a41d2fcd1b9a1"
MOCK_DOCTOR_ID = "6648cb92bc0a41d2fcd1b9a3"
MOCK_ADMIN_ID = "6648cb92bc0a41d2fcd1b9a2"

# Authentication dependency overrides
CURRENT_USER = {
    "id": MOCK_USER_ID,
    "userId": MOCK_USER_ID,
    "email": "user@docton.com",
    "role": "PATIENT",
    "fullName": "Test Patient"
}

async def override_get_current_user():
    return CURRENT_USER

async def override_admin_only():
    return {
        "id": MOCK_ADMIN_ID,
        "userId": MOCK_ADMIN_ID,
        "email": "admin@docton.com",
        "role": "ADMIN",
        "fullName": "Test Admin"
    }

@pytest.fixture(autouse=True)
def setup_overrides():
    # Force reset db in all modules to this file's mock_db to avoid cross-test-file bleeding
    app.database.db = mock_db
    app.services.user.db = mock_db
    app.services.doctor.db = mock_db
    app.services.billing.db = mock_db
    app.services.tracking.db = mock_db
    app.services.auth.db = mock_db
    app.routers.analytics.db = mock_db
    app.routers.auth.db = mock_db
    app.routers.clinical.db = mock_db
    app.routers.doctors.db = mock_db
    app.routers.financial.db = mock_db
    app.routers.nurses.db = mock_db
    app.routers.system.db = mock_db
    app.routers.tasks.db = mock_db
    app.routers.users.db = mock_db
    app.routers.verification.db = mock_db

    global CURRENT_USER
    CURRENT_USER = {
        "id": MOCK_USER_ID,
        "userId": MOCK_USER_ID,
        "email": "user@docton.com",
        "role": "PATIENT",
        "fullName": "Test Patient"
    }
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    fastapi_app.dependency_overrides[admin_only] = override_admin_only
    yield
    fastapi_app.dependency_overrides.clear()


# ==================== TEST SUITES ====================

# 1. USER & AUTHENTICATION ENDPOINTS
def test_user_flow():
    # Setup test OTP entry
    mock_db.otps.docs = [{
        "_id": ObjectId(),
        "email": "test_register@docton.com",
        "otp": "123456",
        "expiresAt": datetime.now(timezone.utc) + timedelta(minutes=10)
    }]

    # A. Register user
    reg_payload = {
        "name": "Register Test",
        "email": "test_register@docton.com",
        "phone": "+919999911111",
        "password": "SecretPassword123",
        "gender": "male",
        "dob": "2000-01-01"
    }
    response = client.post("/api/users/register", json=reg_payload)
    assert response.status_code in [200, 201]
    assert response.json()["success"] is True

    # B. Verify OTP
    verify_payload = {
        "email": "test_register@docton.com",
        "otp": "123456"
    }
    response = client.post("/api/users/verify-otp", json=verify_payload)
    assert response.status_code == 200

    # C. Get Me Profile
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Register Test",
        "email": "user@docton.com",
        "role": "PATIENT"
    }]
    response = client.get("/api/users/me")
    assert response.status_code == 200
    assert response.json()["user"]["email"] == "user@docton.com"

    # D. Get All Users (Admin)
    response = client.get("/api/users/?role=PATIENT&isBlocked=false")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # E. Login (with hashed password validation)
    salt = bcrypt.gensalt(10)
    hashed = bcrypt.hashpw("SecretPassword123".encode("utf-8"), salt).decode("utf-8")
    mock_db.users.docs.append({
        "_id": ObjectId(),
        "email": "login_test@docton.com",
        "password": hashed,
        "role": "PATIENT"
    })
    login_payload = {
        "email": "login_test@docton.com",
        "password": "SecretPassword123"
    }
    response = client.post("/api/users/login", json=login_payload)
    assert response.status_code == 200
    assert "token" in response.json()


def test_auth_router():
    # Test Auth Router Register and Login Handlers
    salt = bcrypt.gensalt(10)
    hashed = bcrypt.hashpw("AdminPass123".encode("utf-8"), salt).decode("utf-8")
    mock_db.admins.docs = [{
        "_id": ObjectId(MOCK_ADMIN_ID),
        "username": "super_admin",
        "password": hashed,
        "role": "ADMIN"
    }]

    # A. Register route
    auth_payload = {
        "role": "admin",
        "username": "super_admin",
        "password": "AdminPass123"
    }
    response = client.post("/api/auth/register", json=auth_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # B. Login route
    response = client.post("/api/auth/login", json=auth_payload)
    assert response.status_code == 200
    assert "token" in response.json()


# 2. DOCTOR & NURSE ROUTERS
def test_doctors_flow():
    global CURRENT_USER
    CURRENT_USER = {
        "id": MOCK_DOCTOR_ID,
        "userId": MOCK_DOCTOR_ID,
        "role": "DOCTOR",
        "username": "dr_smith"
    }

    salt = bcrypt.gensalt(10)
    hashed = bcrypt.hashpw("DocSecret123".encode("utf-8"), salt).decode("utf-8")

    mock_db.doctors.docs = [{
        "_id": ObjectId(MOCK_DOCTOR_ID),
        "username": "dr_smith",
        "password": hashed,
        "name": "Dr. John Smith",
        "specialization": "Cardiologist",
        "verificationStatus": 1,
        "isDeleted": 0,
        "location": {"latitude": 12.9716, "longitude": 77.5946}
    }]

    # A. Login Doctor
    login_payload = {
        "username": "dr_smith",
        "password": "DocSecret123"
    }
    response = client.post("/api/doctors/login", json=login_payload)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # B. Get All Doctors with distance proximity
    response = client.get("/api/doctors/?specialization=Cardiologist&latitude=12.9716&longitude=77.5946")
    assert response.status_code == 200
    assert len(response.json()["doctors"]) > 0

    # C. Get Doctor by ID
    response = client.get(f"/api/doctors/{MOCK_DOCTOR_ID}")
    assert response.status_code == 200
    assert response.json()["doctor"]["name"] == "Dr. John Smith"

    # D. Update Doctor Profile
    update_payload = {
        "bio": "Experienced cardiologist",
        "experience": 15
    }
    response = client.put(f"/api/doctors/{MOCK_DOCTOR_ID}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["doctor"]["experience"] == 15

    # E. Update Availability
    avail_payload = {
        "isOnline": 1,
        "clinicHours": [{"day": "Monday", "start": "09:00", "end": "17:00"}]
    }
    response = client.post("/api/doctors/availability", json=avail_payload)
    assert response.status_code == 200
    assert response.json()["isOnline"] == 1

    # F. Incoming Call
    call_payload = {
        "bookingId": "6648cb92bc0a41d2fcd1b9a4",
        "patientId": MOCK_USER_ID
    }
    response = client.post("/api/doctors/incoming-call", json=call_payload)
    assert response.status_code == 200
    assert response.json()["ringing"] is True


def test_nurses_flow():
    mock_db.nurses.docs = [{
        "_id": ObjectId(),
        "name": "Nurse Joy",
        "skills": "Elderly Care, Injection",
        "verificationStatus": 1,
        "isDeleted": 0,
        "rates": {"hourly": 50.0},
        "location": {"latitude": 12.9716, "longitude": 77.5946}
    }]

    # A. Get Nurses with search options
    response = client.get("/api/nurses/?task=Injection&duration_mode=hourly&max_rate=100.0&latitude=12.9716&longitude=77.5946")
    assert response.status_code == 200
    assert response.json()["count"] > 0

    # B. Get Nurse by ID
    nurse_id = mock_db.nurses.docs[0]["_id"]
    response = client.get(f"/api/nurses/{nurse_id}")
    assert response.status_code == 200
    assert response.json()["nurse"]["name"] == "Nurse Joy"


# 3. ANALYTICS, SYSTEM & TASKS
def test_analytics():
    # A. Revenue stats
    response = client.get("/api/analytics/revenue")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # B. Growth stats
    response = client.get("/api/analytics/growth")
    assert response.status_code == 200
    assert "users" in response.json()["data"]

    # C. Heatmap stats
    response = client.get("/api/analytics/heatmap")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0


def test_system():
    # A. Get banners
    response = client.get("/api/system/banners")
    assert response.status_code == 200

    # B. Get announcements
    response = client.get("/api/system/announcements")
    assert response.status_code == 200

    # C. Post banner (admin)
    response = client.post("/api/system/banners", json={"imageUrl": "http://img.png", "title": "B1"})
    assert response.status_code == 201

    # D. Post announcement (admin)
    ann_payload = {
        "title": "Alert",
        "content": "Update soon",
        "role": "PATIENT"
    }
    response = client.post("/api/system/announcements", json=ann_payload)
    assert response.status_code == 201

    # E. Configurations (admin)
    config_payload = {"maintenanceMode": True, "supportPhone": "+910000000000"}
    response = client.put("/api/system/config", json=config_payload)
    assert response.status_code == 200

    response = client.get("/api/system/config")
    assert response.status_code == 200
    assert response.json()["config"]["maintenanceMode"] is True


def test_tasks():
    # A. Get tasks
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert response.json()["success"] is True

    # B. Update task status
    task_id = ObjectId()
    mock_db.booking_tasks.docs = [{
        "_id": task_id,
        "bookingId": ObjectId(),
        "title": "Vital check",
        "isCompleted": False
    }]
    response = client.put(f"/api/tasks/{task_id}", json={"isCompleted": True})
    assert response.status_code == 200
    assert response.json()["task"]["isCompleted"] is True


# 4. VERIFICATION, CLINICAL & FINANCIALS
def test_verification():
    # Setup doctor in mock db
    mock_db.doctors.docs = [{
        "_id": ObjectId(MOCK_DOCTOR_ID),
        "username": "dr_smith",
        "name": "Dr. John Smith",
        "verificationStatus": 1,
        "isDeleted": 0
    }]
    global CURRENT_USER
    CURRENT_USER = {
        "id": MOCK_DOCTOR_ID,
        "userId": MOCK_DOCTOR_ID,
        "role": "DOCTOR",
        "username": "dr_smith"
    }

    # A. Submit verification document
    response = client.post(
        "/api/verification/submit",
        files={"document": ("license.pdf", b"pdf_data", "application/pdf")}
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    # B. Fetch pending verifications
    v_id = mock_db.provider_verifications.docs[0]["_id"]
    response = client.get("/api/verification/pending")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0

    # C. Update verification status
    response = client.patch(
        f"/api/verification/status/{v_id}",
        json={"status": "APPROVED", "remarks": "Approved license"}
    )
    assert response.status_code == 200


def test_clinical():
    booking_id = ObjectId()
    mock_db.bookings.docs = [{
        "_id": booking_id,
        "userId": ObjectId(MOCK_USER_ID)
    }]

    # A. Create prescription
    presc_payload = {
        "bookingId": str(booking_id),
        "medications": [{
            "name": "Paracetamol",
            "dosage": "500mg",
            "frequency": "1-0-1",
            "duration": "5 days"
        }],
        "advice": "Drink water"
    }
    response = client.post("/api/clinical/prescription", json=presc_payload)
    assert response.status_code == 201
    presc_id = response.json()["prescription"]["_id"]

    # B. Generate prescription PDF
    response = client.get(f"/api/clinical/prescription/pdf/{presc_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

    # C. Create visit report
    report_payload = {
        "bookingId": str(booking_id),
        "vitals": {
            "temperature": "98.6 F",
            "bloodPressure": "120/80"
        },
        "diagnosis": "Mild flu"
    }
    response = client.post("/api/clinical/visit-report", json=report_payload)
    assert response.status_code == 201
    report_id = response.json()["report"]["_id"]

    # D. Generate visit report PDF
    response = client.get(f"/api/clinical/visit-report/pdf/{report_id}")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"


def test_financials():
    # Set up some successful payments and withdrawals with valid ObjectIds
    mock_db.payments.docs = [
        {"_id": ObjectId(), "providerId": ObjectId(MOCK_USER_ID), "status": "SUCCESS", "providerAmount": 100.0},
        {"_id": ObjectId(), "providerId": ObjectId(MOCK_USER_ID), "status": "SUCCESS", "providerAmount": 200.0}
    ]
    mock_db.withdrawals.docs = [
        {"_id": ObjectId(), "providerId": ObjectId(MOCK_USER_ID), "status": "APPROVED", "amount": 50.0},
        {"_id": ObjectId(), "providerId": ObjectId(MOCK_USER_ID), "status": "PENDING", "amount": 20.0}
    ]

    # A. Get earnings summary
    response = client.get("/api/financial/earnings")
    assert response.status_code == 200
    assert response.json()["summary"]["currentBalance"] == 230.0 # 300 - 50 - 20

    # B. Request withdrawal
    withdraw_payload = {
        "amount": 100.0,
        "bankDetails": {
            "accountNumber": "1234567890",
            "ifscCode": "HDFC0001234",
            "bankName": "HDFC Bank",
            "accountHolderName": "Test Patient"
        }
    }
    response = client.post("/api/financial/withdraw", json=withdraw_payload)
    assert response.status_code == 201
    assert response.json()["success"] is True

    # C. Simulate payment split
    sim_payload = {
        "totalAmount": 500.0,
        "bookingId": str(ObjectId()),
        "userId": str(ObjectId()),
        "providerId": str(ObjectId()),
        "providerType": "DOCTOR",
        "paymentMode": "UPI"
    }
    response = client.post("/api/financial/simulate-payment", json=sim_payload)
    assert response.status_code == 200
    assert response.json()["paymentRecord"]["providerAmount"] == 499.0
