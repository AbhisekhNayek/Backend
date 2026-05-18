from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from bson import ObjectId

from app.database import db
from app.middlewares.auth import admin_only

router = APIRouter(prefix="/api/admin", tags=["Admin Controls"])

class ShipPackageRequest(BaseModel):
    remarks: Optional[str] = None

@router.get("/care-packages")
async def get_all_care_packages(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        cursor = db.care_packages.find().sort("triggeredAt", -1)
        packages = await cursor.to_list(length=1000)
        
        for p in packages:
            p["_id"] = str(p["_id"])
            p["userId"] = str(p["userId"])
            if p.get("triggeredAt"):
                p["triggeredAt"] = p["triggeredAt"].isoformat()
            if p.get("shippedAt"):
                p["shippedAt"] = p["shippedAt"].isoformat()
        
        return {
            "success": True,
            "count": len(packages),
            "data": packages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/care-packages/{id}/ship")
async def ship_care_package(
    id: str,
    payload: ShipPackageRequest,
    admin: Dict[str, Any] = Depends(admin_only)
):
    try:
        package = await db.care_packages.find_one({"_id": ObjectId(id)})
        if not package:
            raise HTTPException(status_code=404, detail="Care package record not found")

        # Update status
        await db.care_packages.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "status": "SHIPPED",
                "shippedAt": datetime.now(timezone.utc),
                "remarks": payload.remarks
            }}
        )

        return {
            "success": True,
            "message": "Care package status updated to SHIPPED successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commissions")
async def get_commission_dashboard(admin: Dict[str, Any] = Depends(admin_only)):
    try:
        # Aggregate total bookings payments
        cursor = db.payments.find({"status": "SUCCESS"})
        payments = await cursor.to_list(length=10000)

        total_collected = sum(p.get("totalAmount", 0.0) for p in payments)
        total_commissions = sum(p.get("platformFee", 0.0) for p in payments)
        total_payouts_to_providers = sum(p.get("providerAmount", 0.0) for p in payments)

        return {
            "success": True,
            "commissionRate": "₹1 nominal fee per transaction",
            "stats": {
                "totalBookingsVolume": round(total_collected, 2),
                "totalCommissionsCollected": round(total_commissions, 2),
                "totalProviderPayouts": round(total_payouts_to_providers, 2),
                "transactionCount": len(payments)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
