from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId

from app.database import db
from app.middlewares.auth import get_current_user
from app.services.billing import billing_service

router = APIRouter(prefix="/api/financial", tags=["Financial"])

class BankDetailsRequest(BaseModel):
    accountNumber: str
    ifscCode: str
    bankName: str
    accountHolderName: str

class RequestWithdrawalRequest(BaseModel):
    amount: float = Field(..., ge=1)
    bankDetails: BankDetailsRequest

class SimulatePaymentRequest(BaseModel):
    totalAmount: float = Field(..., ge=0)
    bookingId: str
    userId: str
    providerId: str
    providerType: str
    paymentMode: str

@router.get("/earnings")
async def get_earnings(current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        provider_id = current_user["id"]

        # 1. Fetch successful payments
        payments_cursor = db.payments.find({
            "providerId": ObjectId(provider_id),
            "status": "SUCCESS"
        })
        successful_payments = await payments_cursor.to_list(length=1000)
        total_earnings = sum(p.get("providerAmount", 0.0) for p in successful_payments)

        # 2. Fetch withdrawals
        withdrawals_cursor = db.withdrawals.find({
            "providerId": ObjectId(provider_id)
        }).sort("created_at", -1)
        withdrawals = await withdrawals_cursor.to_list(length=1000)

        total_withdrawn = 0.0
        pending_withdrawal = 0.0

        for w in withdrawals:
            w["_id"] = str(w["_id"])
            w["providerId"] = str(w["providerId"])
            if w.get("created_at"):
                w["created_at"] = w["created_at"].isoformat()
            if w.get("updated_at"):
                w["updated_at"] = w["updated_at"].isoformat()

            status_str = w.get("status", "PENDING").upper()
            if status_str == "APPROVED":
                total_withdrawn += w.get("amount", 0.0)
            elif status_str == "PENDING":
                pending_withdrawal += w.get("amount", 0.0)

        current_balance = round(total_earnings - total_withdrawn - pending_withdrawal, 2)

        return {
            "success": True,
            "summary": {
                "totalEarnings": round(total_earnings, 2),
                "totalWithdrawn": round(total_withdrawn, 2),
                "pendingWithdrawal": round(pending_withdrawal, 2),
                "currentBalance": current_balance
            },
            "withdrawals": withdrawals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/withdraw", status_code=status.HTTP_201_CREATED)
async def withdraw(payload: RequestWithdrawalRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        provider_id = current_user["id"]
        provider_type = current_user.get("role", "DOCTOR")

        # 1. Validate balance
        payments_cursor = db.payments.find({
            "providerId": ObjectId(provider_id),
            "status": "SUCCESS"
        })
        successful_payments = await payments_cursor.to_list(length=1000)
        total_earnings = sum(p.get("providerAmount", 0.0) for p in successful_payments)

        withdrawals_cursor = db.withdrawals.find({
            "providerId": ObjectId(provider_id)
        })
        withdrawals = await withdrawals_cursor.to_list(length=1000)

        total_withdrawn = 0.0
        pending_withdrawal = 0.0

        for w in withdrawals:
            status_str = w.get("status", "PENDING").upper()
            if status_str == "APPROVED":
                total_withdrawn += w.get("amount", 0.0)
            elif status_str == "PENDING":
                pending_withdrawal += w.get("amount", 0.0)

        current_balance = total_earnings - total_withdrawn - pending_withdrawal

        if payload.amount > current_balance:
            raise HTTPException(status_code=400, detail="Insufficient balance")

        # 2. Create withdrawal record
        withdrawal_doc = {
            "providerId": ObjectId(provider_id),
            "providerType": provider_type,
            "amount": payload.amount,
            "status": "PENDING",
            "bankDetails": payload.bankDetails.model_dump(),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        await db.withdrawals.insert_one(withdrawal_doc)
        
        # Serialize fields
        withdrawal_doc["_id"] = str(withdrawal_doc["_id"])
        withdrawal_doc["providerId"] = str(withdrawal_doc["providerId"])
        if withdrawal_doc.get("created_at"):
            withdrawal_doc["created_at"] = withdrawal_doc["created_at"].isoformat()
        if withdrawal_doc.get("updated_at"):
            withdrawal_doc["updated_at"] = withdrawal_doc["updated_at"].isoformat()

        return {"success": True, "withdrawal": withdrawal_doc}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/simulate-payment")
async def simulate_payment(payload: SimulatePaymentRequest, current_user: Dict[str, Any] = Depends(get_current_user)):
    try:
        payment_record = await billing_service.create_payment_record(payload.model_dump())
        return {
            "success": True,
            "message": "Payment split processed successfully",
            "paymentRecord": payment_record
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
