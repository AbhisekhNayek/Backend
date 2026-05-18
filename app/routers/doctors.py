from fastapi import APIRouter, HTTPException, Depends, status, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bson import ObjectId
import math
import uuid

from app.services.doctor import doctor_service
from app.middlewares.auth import get_current_user, role_required
from app.utils.jwt import create_access_token
from app.database import db

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

class DoctorLoginRequest(BaseModel):
    username: str
    password: str

class DoctorProfileUpdate(BaseModel):
    name: Optional[str] = None
    profileImage: Optional[str] = None
    bio: Optional[str] = None
    specialization: Optional[str] = None
    qualifications: Optional[List[str]] = None
    experience: Optional[int] = None
    languages: Optional[List[str]] = None
    licenseNo: Optional[str] = None
    clinicName: Optional[str] = None
    clinicAddress: Optional[str] = None
    isOnline: Optional[int] = None

class ClinicHourSlot(BaseModel):
    day: str       # e.g., Monday
    start: str     # e.g., 09:00
    end: str       # e.g., 17:00

class AvailabilityUpdateRequest(BaseModel):
    isOnline: int  # 0 or 1
    clinicHours: Optional[List[ClinicHourSlot]] = None

class IncomingCallRequest(BaseModel):
    bookingId: str
    patientId: str

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@router.post("/login")
async def login(payload: DoctorLoginRequest):
    try:
        doctor = await doctor_service.login(payload.username, payload.password)
        token = create_access_token({
            "id": doctor["_id"],
            "role": doctor.get("role", "DOCTOR"),
            "username": doctor["username"]
        })
        return {
            "success": True,
            "token": token,
            "doctor": {
                "id": doctor["_id"],
                "username": doctor["username"],
                "name": doctor["name"],
                "role": doctor.get("role", "DOCTOR")
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/")
async def get_all_doctors(
    specialization: Optional[str] = Query(None),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        # Build query
        filter_query = {"isDeleted": 0, "verificationStatus": 1}
        if specialization:
            filter_query["specialization"] = {"$regex": specialization, "$options": "i"}

        cursor = db.doctors.find(filter_query, {"password": 0})
        doctors = await cursor.to_list(length=1000)
        
        populated_docs = []
        for doc in doctors:
            doc["_id"] = str(doc["_id"])
            if doc.get("createdAt"):
                doc["createdAt"] = doc["createdAt"].isoformat()
            if doc.get("updatedAt"):
                doc["updatedAt"] = doc["updatedAt"].isoformat()
            if doc.get("lastLocationAt"):
                doc["lastLocationAt"] = doc["lastLocationAt"].isoformat()

            distance_km = None
            d_loc = doc.get("location", {})
            d_lat = d_loc.get("latitude")
            d_lng = d_loc.get("longitude")

            if latitude is not None and longitude is not None and d_lat is not None and d_lng is not None:
                distance_km = haversine_distance(latitude, longitude, d_lat, d_lng)

            doc["distance_km"] = distance_km
            populated_docs.append(doc)

        # Sort by distance if latitude/longitude coordinates are supplied
        if latitude is not None and longitude is not None:
            populated_docs.sort(
                key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0)
            )

        return {
            "success": True,
            "count": len(populated_docs),
            "doctors": populated_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
async def get_doctor_by_id(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        doctor = await doctor_service.get_doctor_profile(id)
        return {
            "success": True,
            "doctor": doctor
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_profile(
    id: str,
    payload: DoctorProfileUpdate,
    current_user: Dict[str, Any] = Depends(role_required(["DOCTOR", "ADMIN"]))
):
    try:
        if current_user.get("role", "").upper() == "DOCTOR" and current_user.get("id") != id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only update your own profile")

        update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
        doctor = await doctor_service.update_profile(id, update_data)
        return {
            "success": True,
            "message": "Profile updated successfully",
            "doctor": doctor
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/availability")
async def update_availability(
    payload: AvailabilityUpdateRequest,
    current_user: Dict[str, Any] = Depends(role_required(["DOCTOR"]))
):
    try:
        doctor_id = current_user["id"]
        
        # Build update set
        update_set = {
            "isOnline": payload.isOnline,
            "updatedAt": datetime.now(timezone.utc)
        }
        if payload.clinicHours is not None:
            update_set["clinicHours"] = [slot.model_dump() for slot in payload.clinicHours]

        # Update Doctor profile
        updated = await db.doctors.find_one_and_update(
            {"_id": ObjectId(doctor_id)},
            {"$set": update_set},
            projection={"password": 0},
            return_document=True
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Doctor not found")

        updated["_id"] = str(updated["_id"])
        if updated.get("createdAt"):
            updated["createdAt"] = updated["createdAt"].isoformat()
        if updated.get("updatedAt"):
            updated["updatedAt"] = updated["updatedAt"].isoformat()

        return {
            "success": True,
            "message": "Availability updated successfully",
            "isOnline": updated["isOnline"],
            "clinicHours": updated.get("clinicHours", [])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/incoming-call")
async def initiate_incoming_call(
    payload: IncomingCallRequest,
    current_user: Dict[str, Any] = Depends(role_required(["DOCTOR", "NURSE"]))
):
    try:
        call_id = f"CALL-{uuid.uuid4().hex[:8].upper()}"
        
        # Trigger mock dynamic ringing screen
        return {
            "success": True,
            "message": "Consultation call initiated. Ringing patient...",
            "callSessionId": call_id,
            "bookingId": payload.bookingId,
            "patientId": payload.patientId,
            "ringtoneDurationSec": 30,
            "ringing": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
