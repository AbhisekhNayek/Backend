from datetime import datetime
from typing import Dict, Any
from bson import ObjectId

from app.database import db

class BillingService:
    def calculate_split(self, total_amount: float) -> Dict[str, float]:
        # Commission Manager: Payment Gateway splits money (Doctor gets 100% currently, minus ₹1 platform fee).
        platform_fee = 1.00 if total_amount >= 1.00 else 0.00
        provider_amount = round(total_amount - platform_fee, 2)
        return {
            "platformFee": platform_fee,
            "providerAmount": provider_amount
        }

    async def create_payment_record(self, data: Dict[str, Any]) -> Dict[str, Any]:
        total_amount = float(data.get("totalAmount", 0.0))
        booking_id = data.get("bookingId")
        user_id = data.get("userId")
        provider_id = data.get("providerId")
        provider_type = data.get("providerType")
        payment_mode = data.get("paymentMode", "UPI")

        splits = self.calculate_split(total_amount)
        platform_fee = splits["platformFee"]
        provider_amount = splits["providerAmount"]

        payment_doc = {
            "bookingId": ObjectId(booking_id),
            "userId": ObjectId(user_id),
            "providerId": ObjectId(provider_id),
            "providerType": provider_type,
            "totalAmount": total_amount,
            "platformFee": platform_fee,
            "providerAmount": provider_amount,
            "paymentMode": payment_mode,
            "status": "SUCCESS",
            "created_at": datetime.utcnow()
        }

        await db.payments.insert_one(payment_doc)
        
        # Serialize ids as strings for returns
        payment_doc["_id"] = str(payment_doc["_id"])
        payment_doc["bookingId"] = str(payment_doc["bookingId"])
        payment_doc["userId"] = str(payment_doc["userId"])
        payment_doc["providerId"] = str(payment_doc["providerId"])
        if payment_doc.get("created_at"):
            payment_doc["created_at"] = payment_doc["created_at"].isoformat()

        return payment_doc

billing_service = BillingService()
