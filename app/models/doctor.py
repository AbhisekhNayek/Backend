from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel

class DoctorFees(MongoBaseModel):
    video: Optional[float] = Field(default=0.0, ge=0)
    clinic: Optional[float] = Field(default=0.0, ge=0)

class DoctorLocation(MongoBaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class Doctor(MongoBaseModel):
    username: str = Field(..., unique=True, max_length=50)
    role: str = "DOCTOR"
    email: str = Field(..., unique=True)
    phone: Optional[str] = None
    password: str
    isFirstLogin: int = Field(default=1, description="0=No, 1=Yes")
    name: str
    profileImage: Optional[str] = None
    bio: Optional[str] = None
    specialization: Optional[str] = None
    qualifications: List[str] = Field(default_factory=list)
    experience: Optional[int] = Field(default=0, ge=0)
    languages: List[str] = Field(default_factory=list)
    licenseNo: Optional[str] = None
    licenseDocument: Optional[str] = None
    verificationStatus: int = Field(default=0, description="0=PENDING, 1=APPROVED, 2=REJECTED")
    fees: DoctorFees = Field(default_factory=DoctorFees)
    consultationMode: List[str] = Field(default_factory=list, description="VIDEO, CLINIC")
    clinicName: Optional[str] = None
    clinicAddress: Optional[str] = None
    location: DoctorLocation = Field(default_factory=DoctorLocation)
    lastLocationAt: Optional[datetime] = None
    rating: float = 0.0
    totalReviews: int = 0
    isOnline: int = Field(default=0, description="0=OFFLINE, 1=ONLINE")
    isDeleted: int = Field(default=0, description="0=ACTIVE, 1=DELETED")
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
