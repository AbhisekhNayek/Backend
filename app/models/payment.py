from typing import Optional
from datetime import datetime
from pydantic import Field, model_validator
from app.models.base import MongoBaseModel, PyObjectId

class Payment(MongoBaseModel):
    bookingId: PyObjectId = Field(...)
    userId: PyObjectId = Field(...)
    providerType: str = Field(..., description="DOCTOR, NURSE")
    providerId: PyObjectId = Field(...)
    totalAmount: float = Field(..., ge=0)
    platformFee: float = Field(..., ge=0)
    providerAmount: float = Field(..., ge=0)
    paymentMode: str = Field(..., description="UPI, CARD, NET_BANKING, WALLET, CASH")
    gatewayRef: Optional[str] = Field(default=None, max_length=100)
    status: str = Field(default="PENDING", description="SUCCESS, FAILED, PENDING")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_amounts(self) -> 'Payment':
        calculated_total = self.platformFee + self.providerAmount
        # Floating point safety check
        if abs(self.totalAmount - calculated_total) > 0.01:
            raise ValueError("totalAmount must equal platformFee + providerAmount")
        return self
