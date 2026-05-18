from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
import uuid

from app.database import db
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/api/users", tags=["Quick Fill Onboarding"])

class QuickFillRequest(BaseModel):
    provider: str  # google, facebook, truecaller
    token: str
    phone: Optional[str] = None
    gender: Optional[str] = "other"
    dob: Optional[str] = None  # ISO format

@router.post("/quick-fill")
async def quick_fill_onboarding(payload: QuickFillRequest):
    provider_lower = payload.provider.lower()
    if provider_lower not in ["google", "facebook", "truecaller"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid provider. Must be google, facebook, or truecaller."
        )

    # 1. Simulate auto-fetching profile details (Truecaller style API call mock)
    mock_email = f"user.{uuid.uuid4().hex[:6]}@{provider_lower}.com"
    mock_name = f"Quick User ({payload.provider.capitalize()})"
    mock_pic = f"https://api.dicebear.com/7.x/initials/svg?seed={mock_name}"
    
    # Custom values depending on provider
    if provider_lower == "google":
        mock_email = "google.user@gmail.com"
        mock_name = "Alex Mercer (Google)"
    elif provider_lower == "facebook":
        mock_email = "facebook.user@fb.com"
        mock_name = "Alex Mercer (Facebook)"
    elif provider_lower == "truecaller":
        mock_email = "truecaller.user@gmail.com"
        mock_name = "Alex Mercer (Truecaller)"

    # Resolve phone & profile details
    phone = payload.phone or "+919999988888"
    gender = payload.gender or "other"
    dob_raw = payload.dob or "1995-01-01T00:00:00Z"
    
    try:
        dob = datetime.fromisoformat(dob_raw.replace("Z", "+00:00"))
    except ValueError:
        dob = datetime.utcnow()

    # 2. Check if a user with that email already exists
    user = await db.users.find_one({"email": mock_email})
    
    if not user:
        # Create a new user account with auto-verified status
        user_doc = {
            "name": mock_name,
            "email": mock_email,
            "phone": phone,
            "profilePic": mock_pic,
            "gender": gender.lower(),
            "dob": dob,
            "role": "PATIENT",
            "isEmailVerified": True,
            "isPhoneVerified": True,
            "isBlocked": False,
            "isDeleted": False,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "address": {
                "line1": None,
                "line2": None,
                "city": None,
                "state": None,
                "country": "India",
                "pincode": None
            },
            "location": {
                "latitude": None,
                "longitude": None
            }
        }
        await db.users.insert_one(user_doc)
        user = user_doc

    # 3. Issue Access Token
    token = create_access_token({
        "id": str(user["_id"]),
        "role": user.get("role", "PATIENT")
    })

    # Return profile data
    return {
        "success": True,
        "message": f"Successfully authenticated via {payload.provider.capitalize()}",
        "token": token,
        "user": {
            "id": str(user["_id"]),
            "name": user["name"],
            "email": user["email"],
            "phone": user["phone"],
            "profilePic": user.get("profilePic"),
            "gender": user["gender"],
            "dob": user["dob"].isoformat() if isinstance(user["dob"], datetime) else str(user["dob"]),
            "role": user.get("role", "PATIENT")
        }
    }
