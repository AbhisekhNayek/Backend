from typing import Optional
from datetime import datetime
from pydantic import Field, field_validator
import re
from app.models.base import MongoBaseModel, PyObjectId

class Booking(MongoBaseModel):
    bookingType: str = Field(..., description="DOCTOR, NURSE")
    mode: str = Field(..., description="VIDEO, CLINIC, HOME")
    userId: PyObjectId = Field(...)
    providerType: str = Field(..., description="DOCTOR, NURSE")
    providerId: PyObjectId = Field(...)
    bookingDate: datetime = Field(...)
    startTime: str = Field(..., description="HH:mm format")
    endTime: str = Field(..., description="HH:mm format")
    nurseDurationType: Optional[str] = Field(default=None, description="HOURLY, DAILY, MONTHLY")
    nurseDurationValue: Optional[int] = Field(default=None, ge=1)
    status: str = Field(default="PENDING", description="PENDING, CONFIRMED, COMPLETED, CANCELLED")
    chatEnabledAt: Optional[datetime] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @field_validator("startTime", "endTime")
    @classmethod
    def validate_time_format(cls, value: str) -> str:
        if not re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", value):
            raise ValueError("Invalid time format (HH:mm)")
        return value
