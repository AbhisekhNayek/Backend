from typing import Optional
from datetime import datetime, timezone
from pydantic import Field, BaseModel
from app.models.base import MongoBaseModel, PyObjectId

class BankDetails(BaseModel):
    accountNumber: Optional[str] = None
    ifscCode: Optional[str] = None
    bankName: Optional[str] = None
    accountHolderName: Optional[str] = None

class Withdrawal(MongoBaseModel):
    providerId: PyObjectId = Field(...)
    providerType: str = Field(..., description="DOCTOR, NURSE")
    amount: float = Field(..., ge=1)
    status: str = Field(default="PENDING", description="PENDING, APPROVED, REJECTED")
    bankDetails: BankDetails = Field(default_factory=BankDetails)
    transactionId: Optional[str] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
