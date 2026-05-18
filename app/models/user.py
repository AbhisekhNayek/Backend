from typing import Optional
from datetime import datetime, timezone
from pydantic import Field, EmailStr
from app.models.base import MongoBaseModel

class Address(MongoBaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "India"
    pincode: Optional[str] = None

class Location(MongoBaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class User(MongoBaseModel):
    name: Optional[str] = Field(default=None, max_length=50)
    email: str = Field(..., unique=True)
    phone: str = Field(..., unique=True)
    profilePic: Optional[str] = None
    gender: str = Field(..., description="male, female, or other")
    dob: datetime
    password: Optional[str] = None
    role: str = "PATIENT"
    isEmailVerified: bool = False
    isPhoneVerified: bool = False
    address: Optional[Address] = Field(default_factory=Address)
    isBlocked: bool = False
    isDeleted: bool = False
    lastLoginAt: Optional[datetime] = None
    location: Optional[Location] = Field(default_factory=Location)
    lastLocationAt: Optional[datetime] = None
    loginAttempts: int = 0
    lockUntil: Optional[datetime] = None
    appKey: str = "edoc"
    refreshToken: Optional[str] = None
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
