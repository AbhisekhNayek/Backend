from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel

class CarePackage(MongoBaseModel):
    userId: str
    userName: str
    userEmail: str
    userPhone: str
    status: str = "PENDING"  # PENDING, SHIPPED, DELIVERED
    cycleLogId: str
    shippingAddress: str
    triggeredAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    shippedAt: Optional[datetime] = None
    remarks: Optional[str] = None
