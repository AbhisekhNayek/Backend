from typing import Optional
from datetime import datetime
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
    triggeredAt: datetime = Field(default_factory=datetime.utcnow)
    shippedAt: Optional[datetime] = None
    remarks: Optional[str] = None
