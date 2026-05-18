from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.services.doctor import doctor_service
from app.middlewares.auth import get_current_user, role_required
from app.utils.jwt import create_access_token

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

class DoctorLoginRequest(BaseModel):
    username: str
    password: str

class DoctorProfileUpdate(BaseModel):
    name: Optional[str] = None
    profileImage: Optional[str] = None
    bio: Optional[str] = None
    specialization: Optional[str] = None
    qualifications: Optional[List[str]] = None
    experience: Optional[int] = None
    languages: Optional[List[str]] = None
    licenseNo: Optional[str] = None
    clinicName: Optional[str] = None
    clinicAddress: Optional[str] = None
    isOnline: Optional[int] = None

@router.post("/login")
async def login(payload: DoctorLoginRequest):
    try:
        doctor = await doctor_service.login(payload.username, payload.password)
        token = create_access_token({
            "id": doctor["_id"],
            "role": doctor.get("role", "DOCTOR"),
            "username": doctor["username"]
        })
        return {
            "success": True,
            "token": token,
            "doctor": {
                "id": doctor["_id"],
                "username": doctor["username"],
                "name": doctor["name"],
                "role": doctor.get("role", "DOCTOR")
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

@router.get("/")
async def get_all_doctors(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        doctors = await doctor_service.list_doctors()
        return {
            "success": True,
            "count": len(doctors),
            "doctors": doctors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{id}")
async def get_doctor_by_id(id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        doctor = await doctor_service.get_doctor_profile(id)
        return {
            "success": True,
            "doctor": doctor
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{id}")
async def update_profile(
    id: str,
    payload: DoctorProfileUpdate,
    current_user: Dict[str, Any] = Depends(role_required(["DOCTOR", "ADMIN"]))
):
    try:
        # If user is a Doctor, make sure they only update their own profile
        if current_user.get("role", "").upper() == "DOCTOR" and current_user.get("id") != id:
            raise HTTPException(status_code=403, detail="Forbidden: You can only update your own profile")

        # Exclude unset fields from the payload update
        update_data = {k: v for k, v in payload.model_dump(exclude_unset=True).items() if v is not None}
        doctor = await doctor_service.update_profile(id, update_data)
        return {
            "success": True,
            "message": "Profile updated successfully",
            "doctor": doctor
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
