from datetime import datetime, timezone
from typing import Dict, Any
from bson import ObjectId

from app.database import db
from app.services.socket import socket_service

class TrackingService:
    async def update_location(self, user_id: str, latitude: float, longitude: float) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc)
        location_data = {
            "location.latitude": latitude,
            "location.longitude": longitude,
            "lastLocationAt": timestamp
        }

        # Try updating User first
        user = await db.users.find_one_and_update(
            {"_id": ObjectId(user_id)},
            {"$set": location_data},
            return_document=True
        )

        # Try Doctor next
        if not user:
            user = await db.doctors.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": location_data},
                return_document=True
            )
            
        # Try Nurse next
        if not user:
            user = await db.nurses.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": location_data},
                return_document=True
            )

        # Store Location History Breadcrumbs
        if user:
            role = user.get("role", "NURSE" if "skills" in user else "UNKNOWN")
            await db.location_history.insert_one({
                "userId": user_id,
                "role": role,
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp
            })

        # Broadcast update to the live-tracking socket room
        await socket_service.broadcast_to_tracking({
            "userId": user_id,
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp.isoformat()
        })

        if user:
            user["_id"] = str(user["_id"])
            if "password" in user:
                del user["password"]
        return user

    async def log_activity(self, user_id: str, role: str, action: str, details: str = None) -> None:
        """
        Log a major system activity and broadcast it to the admin CCTV room.
        """
        timestamp = datetime.now(timezone.utc)
        log_entry = {
            "userId": user_id,
            "role": role,
            "action": action,
            "details": details,
            "timestamp": timestamp
        }
        await db.activity_logs.insert_one(log_entry)
        
        # Format for socket
        log_entry["_id"] = str(log_entry["_id"])
        log_entry["timestamp"] = timestamp.isoformat()
        
        # Broadcast to admin CCTV
        await socket_service.broadcast_activity(log_entry)

tracking_service = TrackingService()
