from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel

class OTP(MongoBaseModel):
    email: str = Field(...)
    otp: str = Field(...)
    expiresAt: datetime = Field(...)
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
