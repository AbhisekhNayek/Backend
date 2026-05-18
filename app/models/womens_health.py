from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel

class WomensHealthLog(MongoBaseModel):
    userId: str
    startDate: datetime
    endDate: datetime
    cycleLength: int = 28
    notes: Optional[str] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Subscription(MongoBaseModel):
    userId: str
    status: str = "ACTIVE"  # ACTIVE, CANCELLED
    startDate: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    isFreePackageTriggered: bool = False
    paymentMandateSetup: bool = False
    paymentProvider: Optional[str] = None  # razorpay, stripe, upi
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
