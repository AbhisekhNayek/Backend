import bcrypt
from typing import Dict, Any, List, Optional
from bson import ObjectId
from app.database import db

class DoctorService:
    async def list_doctors(self) -> List[Dict[str, Any]]:
        cursor = db.doctors.find({"isDeleted": {"$ne": 1}})
        doctors = await cursor.to_list(length=1000)
        for doc in doctors:
            doc["_id"] = str(doc["_id"])
            if "password" in doc:
                del doc["password"]
        return doctors

    async def get_doctor_profile(self, doctor_id: str) -> Dict[str, Any]:
        doctor = await db.doctors.find_one({"_id": ObjectId(doctor_id), "isDeleted": {"$ne": 1}})
        if not doctor:
            raise ValueError("Doctor not found")
        doctor["_id"] = str(doctor["_id"])
        if "password" in doctor:
            del doctor["password"]
        return doctor

    async def login(self, username: str, password: str) -> Dict[str, Any]:
        doctor = await db.doctors.find_one({"username": username})
        if not doctor:
            raise ValueError("Invalid username or password")

        hashed_password = doctor.get("password")
        if not hashed_password or not bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")):
            raise ValueError("Invalid username or password")

        doctor["_id"] = str(doctor["_id"])
        return doctor

    async def update_profile(self, doctor_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        doctor = await db.doctors.find_one_and_update(
            {"_id": ObjectId(doctor_id)},
            {"$set": update_data},
            return_document=True
        )
        if not doctor:
            raise ValueError("Doctor not found")
        doctor["_id"] = str(doctor["_id"])
        if "password" in doctor:
            del doctor["password"]
        return doctor

doctor_service = DoctorService()
