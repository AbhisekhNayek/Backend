from typing import Optional
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class Vitals(MongoBaseModel):
    temperature: Optional[str] = None
    bloodPressure: Optional[str] = None
    pulseRate: Optional[str] = None
    spO2: Optional[str] = None
    weight: Optional[str] = None

class VisitReport(MongoBaseModel):
    bookingId: PyObjectId = Field(...)
    patientId: PyObjectId = Field(...)
    providerId: PyObjectId = Field(...)
    providerType: str = Field(..., description="DOCTOR, NURSE")
    vitals: Vitals = Field(default_factory=Vitals)
    chiefComplaints: Optional[str] = None
    diagnosis: Optional[str] = None
    observations: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
