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

        # If not a patient user, try updating Doctor
        if not user:
            user = await db.doctors.find_one_and_update(
                {"_id": ObjectId(user_id)},
                {"$set": location_data},
                return_document=True
            )

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

tracking_service = TrackingService()
