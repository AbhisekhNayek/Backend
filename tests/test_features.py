import pytest
from fastapi.testclient import TestClient
from bson import ObjectId
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
import copy
import uuid

# Define our mock collection layer
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

    async def find_one(self, query):
        for doc in self.docs:
            match = True
            for k, v in query.items():
                # Support string representation matching for ObjectId
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)
                
                if isinstance(v, dict):
                    if "$ne" in v and doc_val == v["$ne"]:
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
            for k, v in query.items():
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if isinstance(v, dict):
                    if "$ne" in v and doc_val == v["$ne"]:
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

    async def insert_one(self, doc):
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.docs.append(doc)
        
        # Mock insertion result
        res = MagicMock()
        res.inserted_id = doc["_id"]
        return res

    async def insert_many(self, docs):
        for doc in docs:
            if "_id" not in doc:
                doc["_id"] = ObjectId()
            self.docs.append(doc)
        return MagicMock()

    async def update_one(self, query, update):
        # We need to update the original document reference in self.docs
        for doc in self.docs:
            match = True
            for k, v in query.items():
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if isinstance(v, dict):
                    if "$ne" in v and doc_val == v["$ne"]:
                        match = False
                        break
                elif doc_val != v:
                    match = False
                    break
            if match:
                if "$set" in update:
                    for uk, uv in update["$set"].items():
                        doc[uk] = uv
                return MagicMock(modified_count=1)
        return MagicMock(modified_count=0)

    async def find_one_and_update(self, query, update, projection=None, return_document=True):
        for doc in self.docs:
            match = True
            for k, v in query.items():
                doc_val = self._get_nested(doc, k)
                if isinstance(doc_val, ObjectId) and isinstance(v, str):
                    doc_val = str(doc_val)
                elif isinstance(doc_val, str) and isinstance(v, ObjectId):
                    doc_val = ObjectId(doc_val)

                if isinstance(v, dict):
                    if "$ne" in v and doc_val == v["$ne"]:
                        match = False
                        break
                elif doc_val != v:
                    match = False
                    break
            if match:
                if "$set" in update:
                    for uk, uv in update["$set"].items():
                        doc[uk] = uv
                return copy.deepcopy(doc)
        return None

    async def delete_many(self, query):
        self.docs = []
        return MagicMock(deleted_count=1)


class MockDatabase:
    def __init__(self):
        self.users = MockCollection("users")
        self.nurses = MockCollection("nurses")
        self.doctors = MockCollection("doctors")
        self.care_packages = MockCollection("care_packages")
        self.payments = MockCollection("payments")
        self.womens_health_logs = MockCollection("womens_health_logs")
        self.subscriptions = MockCollection("subscriptions")
        self.ai_sessions = MockCollection("ai_sessions")
        self.activity_logs = MockCollection("activity_logs")
        self.location_history = MockCollection("location_history")

# Override client and database in app
import app.database
import app.services.doctor
import app.services.billing
import app.routers.ai
import app.routers.nurses
import app.routers.womens_health
import app.routers.admin_dashboard
import app.routers.doctors
import app.routers.quick_fill
import app.services.tracking
import app.routers.tracking

mock_db = MockDatabase()

# Patch db variables
app.database.db = mock_db
app.services.doctor.db = mock_db
app.services.billing.db = mock_db
app.routers.ai.db = mock_db
app.routers.nurses.db = mock_db
app.routers.womens_health.db = mock_db
app.routers.admin_dashboard.db = mock_db
app.routers.doctors.db = mock_db
app.routers.quick_fill.db = mock_db
app.services.tracking.db = mock_db
app.routers.tracking.db = mock_db

# Patch admin ping command
app.database.client = MagicMock()
app.database.client.admin.command = AsyncMock(return_value={"ok": 1.0})

# Set up FastAPI dependencies
from app.main import app as fastapi_app
from app.middlewares.auth import get_current_user, admin_only

client = TestClient(fastapi_app)

MOCK_USER_ID = "6648cb92bc0a41d2fcd1b9a1"
MOCK_ADMIN_ID = "6648cb92bc0a41d2fcd1b9a2"

# Dependency override callables
async def override_get_current_user():
    return {
        "id": MOCK_USER_ID,
        "userId": MOCK_USER_ID,
        "email": "user@docton.com",
        "role": "PATIENT",
        "fullName": "Test Patient"
    }

async def override_get_current_doctor():
    return {
        "id": MOCK_USER_ID,
        "userId": MOCK_USER_ID,
        "email": "doctor@docton.com",
        "role": "DOCTOR",
        "fullName": "Dr. Test MD"
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
def setup_dependency_overrides():
    # Force reset db in all modules to this file's mock_db to avoid cross-test-file bleeding
    import app.services.auth
    app.database.db = mock_db
    app.services.doctor.db = mock_db
    app.services.billing.db = mock_db
    app.routers.ai.db = mock_db
    app.routers.nurses.db = mock_db
    app.routers.womens_health.db = mock_db
    app.routers.admin_dashboard.db = mock_db
    app.routers.doctors.db = mock_db
    app.routers.quick_fill.db = mock_db
    app.services.tracking.db = mock_db
    app.routers.tracking.db = mock_db
    app.services.auth.db = mock_db

    # By default mock standard patient auth
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_user
    fastapi_app.dependency_overrides[admin_only] = override_admin_only
    yield
    fastapi_app.dependency_overrides.clear()


# ==================== QUICK FILL / ONBOARDING ====================
def test_quick_fill_google():
    payload = {
        "provider": "google",
        "token": "mock-google-id-token"
    }
    response = client.post("/api/users/quick-fill", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user" in data
    assert data["user"]["email"] == "google.user@gmail.com"

def test_quick_fill_facebook():
    payload = {
        "provider": "facebook",
        "token": "mock-facebook-access-token"
    }
    response = client.post("/api/users/quick-fill", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["name"] == "Alex Mercer (Facebook)"

def test_quick_fill_truecaller():
    payload = {
        "provider": "truecaller",
        "token": "mock-truecaller-payload"
    }
    response = client.post("/api/users/quick-fill", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["user"]["phone"] == "+919999988888"


# ==================== AI HUB (3-in-1 ENGINE) ====================
def test_ai_chatbot_general_recommendation():
    payload = {"message": "I have severe stomach ache and acid reflux"}
    response = client.post("/api/ai/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "response" in data
    assert "recommendationCard" in data
    assert "Gastroenterologist" in data["recommendationCard"]["specialist"]

def test_ai_report_analyst():
    response = client.post(
        "/api/ai/analyze-report",
        files={"file": ("blood_report.pdf", b"CBC Hemoglobin 11.2", "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "aiExplanation" in data
    assert len(data["abnormalities"]) > 0
    assert len(data["otcSuggestions"]) > 0

def test_ai_womens_health_pink():
    payload = {"message": "Should I be worried about irregular periods?"}
    response = client.post("/api/ai/pink-chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "response" in data


# ==================== WOMEN'S HEALTH (PINK MODE) ====================
def test_womens_health_cycle_log_and_care_package():
    # Setup mock user profile in mock_db synchronously
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Alex Patient",
        "email": "user@docton.com",
        "gender": "female"
    }]
    mock_db.care_packages.docs = []
    mock_db.subscriptions.docs = []

    payload = {
        "startDate": "2026-05-18",
        "endDate": "2026-05-23",
        "notes": "Mild cramps"
    }
    response = client.post("/api/womens-health/log", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert data["carePackageAlert"] is True
    assert data["packageDetails"]["status"] == "PENDING"

def test_womens_health_auto_pay():
    payload = {
        "upiId": "alex@ybl",
        "mandateLimit": 150.00
    }
    response = client.post("/api/womens-health/auto-pay", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["mandateLimit"] == 150.00


# ==================== PROXIMITY & AVAILABILITY ====================
def test_nurse_proximity_sorting():
    # Insert mock nurse records with varying distances from Bangalore center synchronously
    mock_db.nurses.docs = [
        {
            "_id": ObjectId(),
            "fullName": "Far Nurse",
            "phoneNumber": "111",
            "isDeleted": 0,
            "verificationStatus": 1,
            "location": {"latitude": 12.9000, "longitude": 77.7000}, # Far
            "hourlyRate": 300,
            "tasks": ["Vital Monitoring"]
        },
        {
            "_id": ObjectId(),
            "fullName": "Near Nurse",
            "phoneNumber": "222",
            "isDeleted": 0,
            "verificationStatus": 1,
            "location": {"latitude": 12.9716, "longitude": 77.5945}, # Near
            "hourlyRate": 250,
            "tasks": ["Wound Dressing"]
        }
    ]

    # Query close to Near Nurse (Bangalore coords)
    response = client.get("/api/nurses?latitude=12.9716&longitude=77.5945")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["nurses"]) == 2
    assert data["nurses"][0]["fullName"] == "Near Nurse" # Proximity sorted correctly

def test_doctor_availability_and_incoming_call():
    # Override current user dependency to doctor role
    fastapi_app.dependency_overrides[get_current_user] = override_get_current_doctor
    
    # Pre-populate doctor in DB so updated doesn't return 404
    mock_db.doctors.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "Dr. Test MD",
        "isOnline": 0
    }]

    payload = {
        "isOnline": 1,
        "clinicHours": [
            {"day": "Monday", "start": "09:00", "end": "12:00"}
        ]
    }
    response = client.post("/api/doctors/availability", json=payload)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["isOnline"] == 1

    # Test consultation incoming call ring
    call_payload = {
        "bookingId": "6648cb92bc0a41d2fcd1b9a9",
        "patientId": "6648cb92bc0a41d2fcd1b9a1"
    }
    response_call = client.post("/api/doctors/incoming-call", json=call_payload)
    assert response_call.status_code == 200
    assert response_call.json()["success"] is True
    assert response_call.json()["ringing"] is True


# ==================== ADMIN PANEL & LOGISTICS ====================
def test_admin_logistics_and_commissions():
    mock_db.care_packages.docs = []
    mock_db.payments.docs = []

    # Create qualifying care package
    pkg_id = ObjectId()
    pkg_doc = {
        "_id": pkg_id,
        "userId": ObjectId(MOCK_USER_ID),
        "userEmail": "user@docton.com",
        "status": "PENDING",
        "remarks": None,
        "triggeredAt": datetime.now(timezone.utc)
    }
    mock_db.care_packages.docs.append(pkg_doc)

    # 1. List qualifying care packages
    response = client.get("/api/admin/care-packages")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["count"] >= 1

    # 2. Ship the package
    ship_payload = {"remarks": "Shipped via DTDC tracking ID: DTDC12345"}
    response_ship = client.patch(f"/api/admin/care-packages/{str(pkg_id)}/ship", json=ship_payload)
    assert response_ship.status_code == 200
    assert response_ship.json()["success"] is True

    # 3. Simulate payment & verify ₹1 split commission in Admin Panel
    payment_payload = {
        "totalAmount": 500.0,
        "bookingId": str(ObjectId()),
        "userId": MOCK_USER_ID,
        "providerId": MOCK_USER_ID,
        "providerType": "DOCTOR",
        "paymentMode": "UPI"
    }
    response_pay = client.post("/api/financial/simulate-payment", json=payment_payload)
    assert response_pay.status_code == 200

    response_commission = client.get("/api/admin/commissions")
    assert response_commission.status_code == 200
    comm_data = response_commission.json()
    assert comm_data["success"] is True
    assert comm_data["stats"]["totalCommissionsCollected"] == 1.00 # Nominal ₹1 platform fee split successfully!


# ==================== CCTV & COMPREHENSIVE TRACKING ====================
def test_cctv_and_historical_tracking():
    # 1. Populating mock database for tracking test
    mock_db.users.docs = [{
        "_id": ObjectId(MOCK_USER_ID),
        "name": "CCTV User",
        "location": {"latitude": 12.9716, "longitude": 77.5945},
        "lastLocationAt": datetime.now(timezone.utc),
        "role": "PATIENT"
    }]
    mock_db.doctors.docs = [{
        "_id": ObjectId(),
        "name": "CCTV Doctor",
        "location": {"latitude": 12.9800, "longitude": 77.6000},
        "lastLocationAt": datetime.now(timezone.utc),
        "isOnline": 1,
        "role": "DOCTOR"
    }]
    mock_db.nurses.docs = [{
        "_id": ObjectId(),
        "name": "CCTV Nurse",
        "location": {"latitude": 12.9900, "longitude": 77.6100},
        "lastLocationAt": datetime.now(timezone.utc),
        "isOnline": 1,
        "role": "NURSE"
    }]
    mock_db.location_history.docs = [{
        "_id": ObjectId(),
        "userId": MOCK_USER_ID,
        "role": "PATIENT",
        "latitude": 12.9716,
        "longitude": 77.5945,
        "timestamp": datetime.now(timezone.utc)
    }]
    mock_db.activity_logs.docs = [{
        "_id": ObjectId(),
        "userId": MOCK_USER_ID,
        "role": "PATIENT",
        "action": "LOGIN",
        "details": "User logged in",
        "timestamp": datetime.now(timezone.utc)
    }]

    # 2. Query active locations including nurses
    response_live = client.get("/api/tracking/admin/live")
    assert response_live.status_code == 200
    live_data = response_live.json()
    assert live_data["success"] is True
    assert len(live_data["users"]) == 1
    assert len(live_data["doctors"]) == 1
    assert len(live_data["nurses"]) == 1
    assert live_data["count"] == 3

    # 3. Query historical location breadcrumbs
    response_hist = client.get(f"/api/tracking/admin/history/{MOCK_USER_ID}")
    assert response_hist.status_code == 200
    hist_data = response_hist.json()
    assert hist_data["success"] is True
    assert len(hist_data["history"]) == 1
    assert hist_data["history"][0]["userId"] == MOCK_USER_ID

    # 4. Query recent system activities
    response_act = client.get("/api/tracking/admin/activities")
    assert response_act.status_code == 200
    act_data = response_act.json()
    assert act_data["success"] is True
    assert len(act_data["activities"]) == 1
    assert act_data["activities"][0]["action"] == "LOGIN"

