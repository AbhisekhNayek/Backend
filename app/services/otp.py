import random
from datetime import datetime, timezone, timedelta
from app.database import db

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

async def save_otp(identifier: str, otp: str, is_email: bool = True):
    key = "email" if is_email else "mobile"
    # Delete any existing OTP for this identifier
    await db.otps.delete_many({key: identifier})
    
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=5)
    otp_doc = {
        key: identifier,
        "otp": otp,
        "expiresAt": expires_at,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    await db.otps.insert_one(otp_doc)
    return otp_doc

async def verify_otp(identifier: str, otp: str, is_email: bool = True) -> bool:
    key = "email" if is_email else "mobile"
    record = await db.otps.find_one({key: identifier, "otp": otp})
    if not record:
        return False
    
    # Check expiry
    expires_at = record.get("expiresAt")
    if expires_at and datetime.now(timezone.utc) > expires_at:
        await db.otps.delete_one({"_id": record["_id"]})
        return False
        
    return True
