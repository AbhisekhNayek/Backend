from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import bcrypt
from app.services.auth import auth_service
from app.utils.jwt import create_access_token
from app.services.otp import generate_otp, save_otp, verify_otp
from app.services.email import send_email
from app.database import db

router = APIRouter(prefix="/api/auth", tags=["Auth"])

class AuthRequest(BaseModel):
    role: str
    username: str
    password: str

@router.post("/register")
async def user_register(payload: AuthRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.username)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_444_NOT_FOUND if hasattr(status, "HTTP_444_NOT_FOUND") else 404,
            detail="Account not found"
        )

    is_match = auth_service.verify_password(payload.password, account.get("password", ""))
    if not is_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"id": str(account["_id"]), "role": payload.role})
    return {
        "success": True,
        "token": token,
        "role": payload.role,
        "id": str(account["_id"])
    }

@router.post("/login")
async def user_login(payload: AuthRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.username)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    is_match = auth_service.verify_password(payload.password, account.get("password", ""))
    if not is_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"id": str(account["_id"]), "role": payload.role})
    return {
        "success": True,
        "token": token,
        "role": payload.role,
        "id": str(account["_id"])
    }

class ForgotPasswordRequest(BaseModel):
    email: str
    role: str

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    password: str
    role: str

class ResendOTPRequest(BaseModel):
    email: str
    role: str

@router.post("/forgot-password")
async def forgot_password(payload: ForgotPasswordRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.email)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
    
    otp = generate_otp()
    await save_otp(payload.email, otp, is_email=True)
    await send_email(payload.email, "Reset Your Password", otp, account.get("name", "User"))
    
    return {
        "success": True,
        "message": "OTP sent to your email successfully."
    }

@router.post("/reset-password")
async def reset_password(payload: ResetPasswordRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.email)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
        
    is_valid = await verify_otp(payload.email, payload.otp, is_email=True)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )
        
    # Delete the verified OTP
    await db.otps.delete_many({"email": payload.email})
    
    # Hash the new password
    salt = bcrypt.gensalt(10)
    hashed_password = bcrypt.hashpw(payload.password.encode("utf-8"), salt).decode("utf-8")
    
    # Update matching collection
    role_upper = payload.role.upper()
    if role_upper in ["USER", "PATIENT"]:
        await db.users.update_one({"email": payload.email}, {"$set": {"password": hashed_password}})
    elif role_upper == "DOCTOR":
        await db.doctors.update_one({"email": payload.email}, {"$set": {"password": hashed_password}})
    elif role_upper == "NURSE":
        # Wait, nurse could be registered by username or email. We find nurse by email and update
        await db.nurses.update_one({"email": payload.email}, {"$set": {"password": hashed_password}})
    elif role_upper == "ADMIN":
        await db.admins.update_one({"email": payload.email}, {"$set": {"password": hashed_password}})
    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported role for password reset"
        )
        
    return {
        "success": True,
        "message": "Password reset successfully."
    }

@router.post("/resend-otp")
async def resend_otp(payload: ResendOTPRequest):
    account = await auth_service.find_account_by_role(payload.role, payload.email)
    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )
        
    otp = generate_otp()
    await save_otp(payload.email, otp, is_email=True)
    await send_email(payload.email, "Verify Your Email", otp, account.get("name", "User"))
    
    return {
        "success": True,
        "message": "OTP resent successfully."
    }

