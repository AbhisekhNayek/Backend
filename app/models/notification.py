from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class Notification(MongoBaseModel):
    recipientId: Optional[PyObjectId] = Field(default=None, description="None if it's a broadcast to all or role-based")
    recipientRole: str = Field(default="ALL", description="USER, DOCTOR, NURSE, ALL")
    title: str = Field(...)
    body: str = Field(...)
    type: str = Field(default="SYSTEM", description="SYSTEM, BOOKING, PAYMENT")
    isRead: bool = Field(default=False, description="Used only for targeted single user notifications")
    readBy: List[PyObjectId] = Field(default_factory=list, description="List of user/provider IDs who read this broadcast")
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
