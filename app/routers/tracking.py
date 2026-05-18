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
async def get_live_locations(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        # Find doctors that are online and have valid locations
        doctor_cursor = db.doctors.find({
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
            "clinicAddress": 1,
            "role": 1
        })
        doctors = await doctor_cursor.to_list(length=1000)
        for doc in doctors:
            doc["_id"] = str(doc["_id"])
            if doc.get("lastLocationAt"):
                doc["lastLocationAt"] = doc["lastLocationAt"].isoformat()

        # Find users with valid locations
        user_cursor = db.users.find({
            "location.latitude": {"$exists": True, "$ne": None},
            "location.longitude": {"$exists": True, "$ne": None}
        }, {
            "name": 1,
            "email": 1,
            "phone": 1,
            "profilePic": 1,
            "location": 1,
            "lastLocationAt": 1,
            "role": 1
        })
        users = await user_cursor.to_list(length=2000)
        for u in users:
            u["_id"] = str(u["_id"])
            if u.get("lastLocationAt"):
                u["lastLocationAt"] = u["lastLocationAt"].isoformat()

        # Find nurses with valid locations
        nurse_cursor = db.nurses.find({
            "isOnline": 1,
            "location.latitude": {"$exists": True, "$ne": None},
            "location.longitude": {"$exists": True, "$ne": None}
        }, {
            "name": 1,
            "username": 1,
            "skills": 1,
            "location": 1,
            "lastLocationAt": 1,
            "isOnline": 1,
            "role": 1
        })
        nurses = await nurse_cursor.to_list(length=1000)
        for n in nurses:
            n["_id"] = str(n["_id"])
            if n.get("lastLocationAt"):
                n["lastLocationAt"] = n["lastLocationAt"].isoformat()

        return {
            "success": True,
            "count": len(doctors) + len(users) + len(nurses),
            "doctors": doctors,
            "users": users,
            "nurses": nurses
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/admin/history/{user_id}")
async def get_location_history(user_id: str, limit: int = 100, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        cursor = db.location_history.find({"userId": user_id}).sort("timestamp", -1).limit(limit)
        history = await cursor.to_list(length=limit)
        for h in history:
            h["_id"] = str(h["_id"])
            if h.get("timestamp"):
                h["timestamp"] = h["timestamp"].isoformat()
        return {
            "success": True,
            "history": history
        }
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error getting history: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.get("/admin/activities")
async def get_recent_activities(limit: int = 50, admin: Dict[str, Any] = Depends(admin_only)):
    try:
        cursor = db.activity_logs.find({}).sort("timestamp", -1).limit(limit)
        activities = await cursor.to_list(length=limit)
        for a in activities:
            a["_id"] = str(a["_id"])
            if a.get("timestamp"):
                a["timestamp"] = a["timestamp"].isoformat()
        return {
            "success": True,
            "activities": activities
        }
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error getting activities: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

