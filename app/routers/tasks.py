from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from bson import ObjectId

from app.database import db
from app.middlewares.auth import get_current_user

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

class UpdateTaskStatusRequest(BaseModel):
    isCompleted: bool

@router.get("")
async def get_tasks(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        user_id = current_user["id"]

        # Run aggregate to fetch tasks that belong to bookings served by this provider
        pipeline = [
            {
                "$lookup": {
                    "from": "bookings",
                    "localField": "bookingId",
                    "foreignField": "_id",
                    "as": "booking"
                }
            },
            {"$unwind": "$booking"},
            {"$match": {"booking.providerId": ObjectId(user_id)}}
        ]
        
        cursor = db.booking_tasks.aggregate(pipeline)
        tasks = await cursor.to_list(length=1000)

        for t in tasks:
            t["_id"] = str(t["_id"])
            t["bookingId"] = str(t["bookingId"])
            if t.get("created_at"):
                t["created_at"] = t["created_at"].isoformat()
            
            # Serialize booking subdocument
            b = t["booking"]
            b["_id"] = str(b["_id"])
            b["userId"] = str(b["userId"])
            b["providerId"] = str(b["providerId"])
            if b.get("bookingDate"):
                b["bookingDate"] = b["bookingDate"].isoformat()
            if b.get("chatEnabledAt"):
                b["chatEnabledAt"] = b["chatEnabledAt"].isoformat()
            if b.get("created_at"):
                b["created_at"] = b["created_at"].isoformat()

        return {"success": True, "tasks": tasks}
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

@router.put("/{id}")
async def update_task_status(id: str, payload: UpdateTaskStatusRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        task = await db.booking_tasks.find_one_and_update(
            {"_id": ObjectId(id)},
            {"$set": {"isCompleted": payload.isCompleted}},
            return_document=True
        )
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        task["_id"] = str(task["_id"])
        task["bookingId"] = str(task["bookingId"])
        if task.get("created_at"):
            task["created_at"] = task["created_at"].isoformat()

        return {"success": True, "task": task}
    except HTTPException as he:
        raise he
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

