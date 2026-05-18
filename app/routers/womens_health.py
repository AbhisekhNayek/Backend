from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
import uuid

from app.database import db
from app.middlewares.auth import get_current_user

router = APIRouter(prefix="/api/womens-health", tags=["Women's Health (Pink Mode)"])

class CycleLogRequest(BaseModel):
    startDate: str  # ISO format
    endDate: str    # ISO format
    notes: Optional[str] = None
    shippingAddress: Optional[str] = None

class AutoPayRequest(BaseModel):
    upiId: Optional[str] = None
    cardNumber: Optional[str] = None
    cardExpiry: Optional[str] = None
    mandateLimit: float = 299.00

@router.post("/log")
async def log_cycle(payload: CycleLogRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["id"]
    
    try:
        start_date = datetime.fromisoformat(payload.startDate.replace("Z", "+00:00"))
        end_date = datetime.fromisoformat(payload.endDate.replace("Z", "+00:00"))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use ISO format.")

    # 1. Fetch user details to verify eligibility (Gender must be female or unspecified, but let's be supportive)
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    # 2. Insert Cycle Log
    cycle_log = {
        "userId": user_id,
        "startDate": start_date,
        "endDate": end_date,
        "cycleLength": (end_date - start_date).days,
        "notes": payload.notes,
        "createdAt": datetime.utcnow()
    }
    log_res = await db.womens_health_logs.insert_one(cycle_log)
    log_id = str(log_res.inserted_id)

    # 3. Check for Free Care Package Eligibility (1st month is promo 100% OFF)
    # Check if a care package already exists for this user
    existing_package = await db.care_packages.find_one({"userId": user_id})
    care_package_triggered = False
    package_details = None

    # We trigger the care package if gender is female and they have no prior packages
    user_gender = user.get("gender", "").lower()
    if not existing_package and user_gender in ["female", "other"]:
        shipping_addr = payload.shippingAddress or user.get("address", {}).get("line1") or "User Address on file"
        
        # Trigger PENDING care package
        care_package_doc = {
            "userId": user_id,
            "userName": user.get("name", "Valued User"),
            "userEmail": user["email"],
            "userPhone": user.get("phone", "N/A"),
            "status": "PENDING",
            "cycleLogId": log_id,
            "shippingAddress": shipping_addr,
            "triggeredAt": datetime.utcnow(),
            "remarks": "First log campaign eligibility qualified."
        }
        await db.care_packages.insert_one(care_package_doc)
        
        # Save subscription state
        subscription_doc = {
            "userId": user_id,
            "status": "ACTIVE",
            "startDate": datetime.utcnow(),
            "isFreePackageTriggered": True,
            "paymentMandateSetup": False,
            "createdAt": datetime.utcnow()
        }
        await db.subscriptions.insert_one(subscription_doc)
        
        care_package_triggered = True
        package_details = {
            "status": "PENDING",
            "campaign": "First Month Free Wellness Care Package",
            "shippingAddress": shipping_addr
        }

    # Format return log
    cycle_log["_id"] = log_id
    cycle_log["startDate"] = cycle_log["startDate"].isoformat()
    cycle_log["endDate"] = cycle_log["endDate"].isoformat()
    cycle_log["createdAt"] = cycle_log["createdAt"].isoformat()

    return {
        "success": True,
        "message": "Cycle logged successfully.",
        "data": cycle_log,
        "carePackageAlert": care_package_triggered,
        "packageDetails": package_details
    }

@router.post("/auto-pay")
async def register_auto_pay(payload: AutoPayRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    user_id = current_user["id"]
    
    if not payload.upiId and not payload.cardNumber:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must specify either a upiId or a cardNumber/expiry to setup e-mandate."
        )

    # 1. Update subscription status
    mandate_id = f"MND-{uuid.uuid4().hex[:8].upper()}"
    provider = "UPI" if payload.upiId else "CARD"

    # Find subscription
    subscription = await db.subscriptions.find_one({"userId": user_id})
    if subscription:
        await db.subscriptions.update_one(
            {"userId": user_id},
            {"$set": {
                "paymentMandateSetup": True,
                "paymentProvider": provider,
                "mandateId": mandate_id,
                "mandateLimit": payload.mandateLimit
            }}
        )
    else:
        # Create subscription with mandate setup
        await db.subscriptions.insert_one({
            "userId": user_id,
            "status": "ACTIVE",
            "startDate": datetime.utcnow(),
            "isFreePackageTriggered": False,
            "paymentMandateSetup": True,
            "paymentProvider": provider,
            "mandateId": mandate_id,
            "mandateLimit": payload.mandateLimit,
            "createdAt": datetime.utcnow()
        })

    return {
        "success": True,
        "message": f"Auto-pay e-mandate via {provider} registered successfully. Subsequent cycles will be auto-debited.",
        "mandateId": mandate_id,
        "mandateLimit": payload.mandateLimit
    }
