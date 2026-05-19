from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel

class NurseRates(MongoBaseModel):
    hourly: Optional[float] = Field(default=0.0, ge=0)
    daily: Optional[float] = Field(default=0.0, ge=0)
    monthly: Optional[float] = Field(default=0.0, ge=0)

class NurseLocation(MongoBaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Nurse(MongoBaseModel):
    username: str = Field(..., unique=True, max_length=50)
    password: str
    isFirstLogin: int = Field(default=1, description="0=No, 1=Yes")
    name: Optional[str] = Field(default=None, max_length=50)
    profileImage: Optional[str] = None
    skills: Optional[str] = Field(default=None, max_length=200)
    experience: Optional[int] = Field(default=0, ge=0)
    rates: NurseRates = Field(default_factory=NurseRates)
    location: NurseLocation = Field(default_factory=NurseLocation)
    lastLocationAt: Optional[datetime] = None
    isOnline: int = Field(default=0, description="0=OFFLINE, 1=ONLINE")
    verificationStatus: int = Field(default=0, description="0=PENDING, 1=APPROVED, 2=REJECTED")
    isDeleted: int = Field(default=0, description="0=ACTIVE, 1=DELETED")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
