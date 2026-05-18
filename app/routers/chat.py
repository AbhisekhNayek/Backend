from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.chat import chat_service
from app.middlewares.auth import get_current_user

router = APIRouter(prefix="/api/chat", tags=["Chat"])

class AttachmentRequest(BaseModel):
    url: str
    fileType: Optional[str] = None
    name: Optional[str] = None

class SendMessageRequest(BaseModel):
    receiverId: str
    text: Optional[str] = None
    attachments: Optional[List[AttachmentRequest]] = None

@router.get("/recent")
async def get_recent(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        chats = await chat_service.get_recent_chats(current_user["id"])
        return {"success": True, "data": chats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history/{partnerId}")
async def get_history(partnerId: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        history = await chat_service.get_history(current_user["id"], partnerId)
        return {"success": True, "data": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send", status_code=status.HTTP_201_CREATED)
async def send_msg(payload: SendMessageRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        attachments_data = []
        if payload.attachments:
            attachments_data = [att.model_dump() for att in payload.attachments]
            
        message = await chat_service.send_message(
            sender_id=current_user["id"],
            receiver_id=payload.receiverId,
            text=payload.text,
            attachments=attachments_data
        )
        return {"success": True, "data": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
