import bcrypt
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
from bson import ObjectId

from app.database import db
from app.utils.jwt import create_access_token
from app.services.otp import generate_otp, save_otp
from app.services.email import send_email

class UserService:
    async def register(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        email = user_data.get("email")
        name = user_data.get("name")
        phone = user_data.get("phone")
        password = user_data.get("password")
        gender = user_data.get("gender")
        dob_raw = user_data.get("dob")

        # Parse dob
        if isinstance(dob_raw, str):
            try:
                dob = datetime.fromisoformat(dob_raw.replace("Z", "+00:00"))
            except ValueError:
                dob = datetime.now(timezone.utc)
        elif isinstance(dob_raw, datetime):
            dob = dob_raw
        else:
            dob = datetime.now(timezone.utc)

        existing = await db.users.find_one({"email": email})
        if existing:
            raise ValueError("User already exists")

        # Hash password
        salt = bcrypt.gensalt(10)
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

        user_doc = {
            "name": name,
            "email": email,
            "phone": phone,
            "password": hashed_password,
            "gender": gender,
            "dob": dob,
            "role": "PATIENT",
            "isEmailVerified": False,
            "isPhoneVerified": False,
            "isBlocked": False,
            "isDeleted": False,
            "createdAt": datetime.now(timezone.utc),
            "updatedAt": datetime.now(timezone.utc),
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

        otp = generate_otp()
        await save_otp(email, otp, is_email=True)
        await send_email(email, "Verify Your Email", otp, name)

        return {"success": True, "message": "User registered. OTP sent to email."}

    async def verify_otp(self, email: str, otp: str) -> Dict[str, Any]:
        record = await db.otps.find_one({"email": email, "otp": otp})
        if not record or record.get("expiresAt") < datetime.now(timezone.utc):
            raise ValueError("Invalid or expired OTP")

        await db.users.update_one({"email": email}, {"$set": {"isEmailVerified": True}})
        await db.otps.delete_one({"_id": record["_id"]})

        return {"success": True, "message": "Email verified successfully"}

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        user = await db.users.find_one({"email": email})
        if not user:
            raise ValueError("Invalid credentials")

        hashed_password = user.get("password")
        if not hashed_password or not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            raise ValueError("Invalid credentials")

        token = create_access_token({"id": str(user["_id"]), "role": user.get("role", "PATIENT")})

        await db.users.update_one(
            {"_id": user["_id"]},
            {"$set": {"lastLoginAt": datetime.now(timezone.utc)}}
        )

        return {"success": True, "token": token}

    async def get_profile(self, user_id: str) -> Dict[str, Any]:
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise ValueError("User not found")
        # Ensure _id is string for JSON responses
        user["_id"] = str(user["_id"])
        if "password" in user:
            del user["password"]
        return user

user_service = UserService()
