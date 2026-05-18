import bcrypt
from typing import Dict, Any, Optional
from app.database import db

class AuthService:
    async def find_account_by_role(self, role: str, username: str) -> Optional[Dict[str, Any]]:
        role_upper = role.upper()
        if role_upper == "USER":
            # Match both phone/mobile for patient accounts to be robust
            return await db.users.find_one({
                "$or": [
                    {"phone": username},
                    {"mobile": username},
                    {"email": username}
                ]
            })
        elif role_upper == "ADMIN":
            return await db.admins.find_one({"username": username})
        elif role_upper == "DOCTOR":
            return await db.doctors.find_one({"username": username})
        elif role_upper == "NURSE":
            return await db.nurses.find_one({"username": username})
        return None

    def verify_password(self, plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

auth_service = AuthService()
