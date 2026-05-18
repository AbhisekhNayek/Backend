from fastapi import APIRouter, Request, HTTPException
import hashlib
import json
from bson import ObjectId

from app.config import settings
from app.utils.zego_token import generate_token04
from app.database import db

router = APIRouter(prefix="/api/video", tags=["Video Calling"])

@router.get("/token")
async def get_video_token(userId: str, roomId: str):
    """
    Generate a secure ZEGOCLOUD room access token (token04)
    """
    if not settings.zego_app_id or not settings.zego_callback_secret:
        raise HTTPException(status_code=500, detail="ZEGOCLOUD credentials not configured on server")

    # Generate token payload with strict access permissions
    payload = {
        "room_id": roomId,
        "privilege": {1: 1, 2: 1}, # 1: Login, 2: Publish
        "stream_id_list": None
    }
    
    token_info = generate_token04(
        app_id=settings.zego_app_id,
        user_id=userId,
        secret=settings.zego_callback_secret,
        effective_time_in_seconds=3600,
        payload=json.dumps(payload)
    )
    
    if token_info.error_code != 0:
        raise HTTPException(status_code=500, detail=f"Token generation failed: {token_info.error_message}")
        
    return {
        "success": True,
        "appId": settings.zego_app_id,
        "appSign": settings.zego_app_sign,  # Useful for older SDKs
        "token": token_info.token
    }

@router.post("/webhook")
async def zegocloud_webhook(request: Request, timestamp: str = "", nonce: str = "", signature: str = ""):
    """
    Handle ZEGOCLOUD Server-to-Server callbacks
    """
    if not settings.zego_callback_secret:
        raise HTTPException(status_code=500, detail="ZEGOCLOUD webhook secret not configured")
        
    # 1. Signature Validation (SHA-1 over sorted array of [secret, timestamp, nonce])
    params = [settings.zego_callback_secret, timestamp, nonce]
    params.sort()
    joined_str = "".join(params)
    
    computed_signature = hashlib.sha1(joined_str.encode('utf-8')).hexdigest()
    if computed_signature != signature:
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    # 2. Process callback event payload
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    event = body.get("event")
    room_id = body.get("room_id")
    
    # 3. Synchronize Booking State on Call Completion
    if event == "room_close" and room_id:
        try:
            if ObjectId.is_valid(room_id):
                await db.bookings.update_one(
                    {"_id": ObjectId(room_id)},
                    {"$set": {"status": "COMPLETED"}}
                )
        except Exception as e:
            print(f"[ZEGO Webhook] Error updating booking status: {e}")
            
    return {"success": True, "message": "Webhook processed successfully"}
