from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any

from app.services.tracking import tracking_service
from app.middlewares.auth import get_current_user, admin_only
from app.database import db

router = APIRouter(prefix="/api/tracking", tags=["Tracking"])

class LocationUpdateRequest(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)

@router.post("/update")
async def update_location(payload: LocationUpdateRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        user = await tracking_service.update_location(
            current_user["id"],
            payload.latitude,
            payload.longitude
        )
        if not user:
            raise HTTPException(status_code=404, detail="Account not found")

        return {
            "success": True,
            "message": "Location updated",
            "location": user.get("location", {})
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/admin/live")
async def get_live_doctors(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        # Find doctors that are online and have valid locations
        cursor = db.doctors.find({
            "isOnline": 1,
            "location.latitude": {"$exists": True, "$ne": None},
            "location.longitude": {"$exists": True, "$ne": None}
        }, {
            "name": 1,
            "email": 1,
            "phone": 1,
            "specialization": 1,
            "profileImage": 1,
            "location": 1,
            "lastLocationAt": 1,
            "isOnline": 1,
            "clinicName": 1,
            "clinicAddress": 1
        })
        doctors = await cursor.to_list(length=1000)
        for doc in doctors:
            doc["_id"] = str(doc["_id"])
            if doc.get("lastLocationAt"):
                doc["lastLocationAt"] = doc["lastLocationAt"].isoformat()

        return {
            "success": True,
            "count": len(doctors),
            "data": doctors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
