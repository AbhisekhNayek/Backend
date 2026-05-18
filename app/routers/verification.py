from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.database import db
from app.middlewares.auth import get_current_user, admin_only
from app.services.storage import storage_service

router = APIRouter(prefix="/api/verification", tags=["Verification"])

class UpdateStatusRequest(BaseModel):
    status: str
    remarks: Optional[str] = None

@router.post("/submit")
async def submit_verification(
    document: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    try:
        doctor_id = current_user["id"]
        
        # 1. Read file bytes
        file_bytes = await document.read()
        
        # 2. Upload to S3
        document_url = storage_service.upload_file(
            file_content=file_bytes,
            original_filename=document.filename,
            mimetype=document.content_type or "application/octet-stream",
            folder="verifications"
        )

        # 3. Update Doctor verificationStatus to 0 (PENDING) and licenseDocument
        doctor = await db.doctors.find_one_and_update(
            {"_id": ObjectId(doctor_id)},
            {"$set": {
                "verificationStatus": 0,
                "licenseDocument": document_url
            }},
            return_document=True
        )
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

        # 4. Create ProviderVerification record
        verification_doc = {
            "providerType": "DOCTOR",
            "providerId": ObjectId(doctor_id),
            "documentUrl": document_url,
            "status": "PENDING",
            "adminId": None,
            "remarks": None,
            "created_at": datetime.now(timezone.utc)
        }
        await db.provider_verifications.insert_one(verification_doc)

        return {
            "success": True,
            "message": "Verification document submitted successfully",
            "documentUrl": document_url
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending")
async def get_pending_verifications(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        # Find all pending provider verifications
        cursor = db.provider_verifications.find({"status": "PENDING"})
        verifications = await cursor.to_list(length=1000)

        # Populate providerId details
        populated_verifications = []
        for v in verifications:
            v["_id"] = str(v["_id"])
            provider_id = v["providerId"]
            v["providerId"] = str(provider_id)
            if v.get("created_at"):
                v["created_at"] = v["created_at"].isoformat()

            # Query doctors collection
            doctor = await db.doctors.find_one(
                {"_id": provider_id},
                {"name": 1, "email": 1, "specialization": 1, "licenseNo": 1, "profileImage": 1}
            )
            if doctor:
                doctor["_id"] = str(doctor["_id"])
                v["providerDetails"] = doctor
            else:
                v["providerDetails"] = None

            populated_verifications.append(v)

        return {
            "success": True,
            "data": populated_verifications
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/status/{id}")
async def update_verification_status(
    id: str,
    payload: UpdateStatusRequest,
    admin: Dict[str, Any] = Depends(admin_only)
):
    try:
        status_upper = payload.status.upper()
        if status_upper not in ["APPROVED", "REJECTED"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be APPROVED or REJECTED.")

        # Find verification record
        verification = await db.provider_verifications.find_one({"_id": ObjectId(id)})
        if not verification:
            raise HTTPException(status_code=404, detail="Verification record not found")

        # Update verification record
        await db.provider_verifications.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "status": status_upper,
                "remarks": payload.remarks,
                "adminId": ObjectId(admin["id"]),
                "updated_at": datetime.now(timezone.utc)
            }}
        )

        # Update provider's verification status
        provider_status = 1 if status_upper == "APPROVED" else 2
        await db.doctors.update_one(
            {"_id": verification["providerId"]},
            {"$set": {"verificationStatus": provider_status}}
        )

        return {
            "success": True,
            "message": f"Provider {status_upper.lower()} successfully"
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
