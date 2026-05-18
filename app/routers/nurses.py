from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
import math

from app.database import db
from app.middlewares.auth import get_current_user

router = APIRouter(prefix="/api/nurses", tags=["Nurses"])

class BookingRates(BaseModel):
    hourly: Optional[float] = None
    daily: Optional[float] = None
    monthly: Optional[float] = None

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    # Radius of the Earth in km
    R = 6371.0
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

@router.get("/")
async def get_nurses(
    task: Optional[str] = Query(None, description="Comma-separated skills/tasks, e.g. Injection,Elderly Care"),
    duration_mode: Optional[str] = Query(None, description="hourly, daily, or monthly"),
    max_rate: Optional[float] = Query(None, description="Maximum price based on duration mode"),
    latitude: Optional[float] = Query(None),
    longitude: Optional[float] = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        filter_query = {
            "isDeleted": 0,
            "verificationStatus": 1  # Only verified nurses
        }

        # 1. Filter by skills/tasks
        if task:
            task_list = [t.strip().lower() for t in task.split(",") if t.strip()]
            # Match if skills string contains any of the requested tasks
            or_filters = [{"skills": {"$regex": t, "$options": "i"}} for t in task_list]
            if or_filters:
                filter_query["$or"] = or_filters

        # 2. Filter by rate thresholds
        if duration_mode:
            duration_lower = duration_mode.lower()
            if duration_lower in ["hourly", "daily", "monthly"] and max_rate is not None:
                filter_query[f"rates.{duration_lower}"] = {"$lte": max_rate, "$gt": 0}

        cursor = db.nurses.find(filter_query, {"password": 0})
        nurses = await cursor.to_list(length=1000)

        # 3. Sort by proximity if coordinates are supplied
        populated_nurses = []
        for n in nurses:
            n["_id"] = str(n["_id"])
            if n.get("created_at"):
                n["created_at"] = n["created_at"].isoformat()
            if n.get("lastLocationAt"):
                n["lastLocationAt"] = n["lastLocationAt"].isoformat()

            distance_km = None
            n_loc = n.get("location", {})
            n_lat = n_loc.get("latitude")
            n_lng = n_loc.get("longitude")

            if latitude is not None and longitude is not None and n_lat is not None and n_lng is not None:
                distance_km = haversine_distance(latitude, longitude, n_lat, n_lng)
            
            n["distance_km"] = distance_km
            populated_nurses.append(n)

        # Proximity sorting (closest first)
        if latitude is not None and longitude is not None:
            # Put nurses with location first, sorted by distance, followed by nurses without location
            populated_nurses.sort(
                key=lambda x: (x["distance_km"] is None, x["distance_km"] or 0)
            )

        return {
            "success": True,
            "count": len(populated_nurses),
            "nurses": populated_nurses
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
async def get_nurse_by_id(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        nurse = await db.nurses.find_one({"_id": ObjectId(id)}, {"password": 0})
        if not nurse:
            raise HTTPException(status_code=404, detail="Nurse profile not found")

        nurse["_id"] = str(nurse["_id"])
        if nurse.get("created_at"):
            nurse["created_at"] = nurse["created_at"].isoformat()
        if nurse.get("lastLocationAt"):
            nurse["lastLocationAt"] = nurse["lastLocationAt"].isoformat()

        return {
            "success": True,
            "nurse": nurse
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
