from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone
from bson import ObjectId

from app.database import db
from app.middlewares.auth import get_current_user, admin_only
from app.services.socket import socket_service

router = APIRouter(tags=["Notifications"])

class AdminNotificationRequest(BaseModel):
    recipientId: Optional[str] = None
    recipientRole: str = "ALL" # USER, DOCTOR, NURSE, ALL
    title: str
    body: str
    type: str = "SYSTEM" # SYSTEM, BOOKING, PAYMENT

@router.post("/api/admin/notifications/send")
async def send_notification(
    payload: AdminNotificationRequest,
    admin: Dict[str, Any] = Depends(admin_only)
):
    try:
        notification_data = {
            "title": payload.title,
            "body": payload.body,
            "type": payload.type,
            "createdAt": datetime.now(timezone.utc)
        }
        
        # 1. Targeted Notification
        if payload.recipientId:
            recipient_oid = ObjectId(payload.recipientId)
            
            # Verify recipient exists & find their role
            recipient = None
            role = None
            for r, col in [("USER", db.users), ("DOCTOR", db.doctors), ("NURSE", db.nurses)]:
                res = await col.find_one({"_id": recipient_oid})
                if res:
                    recipient = res
                    role = r
                    break
            
            if not recipient:
                raise HTTPException(status_code=404, detail="Recipient not found")
                
            notification_data["recipientId"] = recipient_oid
            notification_data["recipientRole"] = role
            notification_data["isRead"] = False
            notification_data["readBy"] = []
            
            # Insert to DB
            insert_res = await db.notifications.insert_one(notification_data)
            notification_data["_id"] = str(insert_res.inserted_id)
            notification_data["recipientId"] = str(recipient_oid)
            notification_data["createdAt"] = notification_data["createdAt"].isoformat()
            
            # Emit in real-time
            await socket_service.emit_to_user(payload.recipientId, "new_notification", notification_data)
            
        # 2. Broadcast Notification
        else:
            role_upper = payload.recipientRole.upper()
            if role_upper not in ["USER", "PATIENT", "DOCTOR", "NURSE", "ALL"]:
                raise HTTPException(status_code=400, detail="Invalid target role")
                
            # Keep patient aligned with standard role USER
            if role_upper == "PATIENT":
                role_upper = "USER"
                
            notification_data["recipientId"] = None
            notification_data["recipientRole"] = role_upper
            notification_data["isRead"] = False
            notification_data["readBy"] = []
            
            # Insert to DB
            insert_res = await db.notifications.insert_one(notification_data)
            notification_data["_id"] = str(insert_res.inserted_id)
            notification_data["createdAt"] = notification_data["createdAt"].isoformat()
            
            # Emit globally or to role
            if role_upper == "ALL":
                await socket_service.broadcast_to_all("new_notification", notification_data)
            else:
                await socket_service.broadcast_to_role(role_upper, "new_notification", notification_data)
                
        return {
            "success": True,
            "message": "Notification sent successfully",
            "data": notification_data
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f"Error sending notification: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/notifications")
async def get_my_notifications(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        user_id = current_user.get("id")
        user_oid = ObjectId(user_id)
        role = current_user.get("role", "UNKNOWN").upper()
        if role == "PATIENT":
            role = "USER"
            
        # Find direct and broadcast notifications
        query = {
            "$or": [
                {"recipientId": user_oid},
                {
                    "recipientId": None,
                    "recipientRole": {"$in": [role, "ALL"]}
                }
            ]
        }
        
        cursor = db.notifications.find(query).sort("createdAt", -1)
        notifications = await cursor.to_list(length=500)
        
        formatted_notifications = []
        for n in notifications:
            is_read = False
            if n.get("recipientId") is not None:
                is_read = n.get("isRead", False)
            else:
                is_read = user_oid in n.get("readBy", [])
                
            formatted_notifications.append({
                "id": str(n["_id"]),
                "recipientId": str(n["recipientId"]) if n.get("recipientId") else None,
                "recipientRole": n.get("recipientRole"),
                "title": n.get("title"),
                "body": n.get("body"),
                "type": n.get("type"),
                "isRead": is_read,
                "createdAt": n.get("createdAt").isoformat() if n.get("createdAt") else None
            })
            
        return {
            "success": True,
            "count": len(formatted_notifications),
            "data": formatted_notifications
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f"Error fetching notifications: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.patch("/api/notifications/{id}/read")
async def mark_as_read(
    id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        notif_oid = ObjectId(id)
        user_id = current_user.get("id")
        user_oid = ObjectId(user_id)
        
        notification = await db.notifications.find_one({"_id": notif_oid})
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
            
        # If direct notification
        if notification.get("recipientId") is not None:
            if notification["recipientId"] != user_oid:
                raise HTTPException(status_code=403, detail="Access denied")
            await db.notifications.update_one({"_id": notif_oid}, {"$set": {"isRead": True}})
        # If broadcast notification
        else:
            await db.notifications.update_one(
                {"_id": notif_oid},
                {"$addToSet": {"readBy": user_oid}}
            )
            
        return {
            "success": True,
            "message": "Notification marked as read successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f"Error marking notification as read: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post("/api/notifications/read-all")
async def mark_all_as_read(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        user_id = current_user.get("id")
        user_oid = ObjectId(user_id)
        role = current_user.get("role", "UNKNOWN").upper()
        if role == "PATIENT":
            role = "USER"
            
        # 1. Update direct notifications
        await db.notifications.update_many(
            {"recipientId": user_oid, "isRead": False},
            {"$set": {"isRead": True}}
        )
        
        # 2. Update broadcast notifications
        await db.notifications.update_many(
            {
                "recipientId": None,
                "recipientRole": {"$in": [role, "ALL"]},
                "readBy": {"$ne": user_oid}
            },
            {"$addToSet": {"readBy": user_oid}}
        )
        
        return {
            "success": True,
            "message": "All notifications marked as read successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f"Error marking all notifications as read: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
