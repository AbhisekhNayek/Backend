from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime

from app.services.user import user_service
from app.services.tracking import tracking_service
from app.middlewares.auth import get_current_user, admin_only
from app.database import db

router = APIRouter(prefix="/api/users", tags=["Users"])

class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str
    gender: str
    dob: str  # ISO format string

class OTPVerifyRequest(BaseModel):
    email: EmailStr
    otp: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: UserRegisterRequest):
    try:
        res = await user_service.register(payload.model_dump())
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify-otp")
async def verify_otp(payload: OTPVerifyRequest):
    try:
        res = await user_service.verify_otp(payload.email, payload.otp)
        return res
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(payload: UserLoginRequest):
    try:
        res = await user_service.login(payload.email, payload.password)
        
        # Log activity
        if res and res.get("user") and res.get("user").get("id"):
            await tracking_service.log_activity(
                user_id=res["user"]["id"],
                role=res["user"].get("role", "USER"),
                action="LOGIN",
                details="User logged in"
            )
            
        return res
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/me")
async def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        user = await user_service.get_profile(current_user["id"])
        return {"success": True, "user": user}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/")
async def get_all_users(
    role: Optional[str] = Query(None),
    isBlocked: Optional[str] = Query(None),
    isDeleted: Optional[str] = Query(None),
    admin: Dict[str, Any] = Depends(admin_only)
):
    try:
        filter_query = {}
        if role:
            filter_query["role"] = role
        if isBlocked is not None:
            filter_query["isBlocked"] = isBlocked.lower() == "true"
        if isDeleted is not None:
            filter_query["isDeleted"] = isDeleted.lower() == "true"

        cursor = db.users.find(filter_query, {"password": 0, "refreshToken": 0}).sort("createdAt", -1)
        users = await cursor.to_list(length=1000)
        for u in users:
            u["_id"] = str(u["_id"])
            if u.get("createdAt"):
                u["createdAt"] = u["createdAt"].isoformat()
            if u.get("updatedAt"):
                u["updatedAt"] = u["updatedAt"].isoformat()
            if u.get("dob"):
                u["dob"] = u["dob"].isoformat()
            if u.get("lastLoginAt") and isinstance(u["lastLoginAt"], datetime):
                u["lastLoginAt"] = u["lastLoginAt"].isoformat()

        return {
            "success": True,
            "count": len(users),
            "data": users
        }
    except HTTPException:
        raise
    except Exception as e:
        from app.logger import logger
        logger.error(f'Unhandled error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail='Internal Server Error')

