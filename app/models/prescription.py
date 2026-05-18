from typing import Optional, List
from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class Medication(MongoBaseModel):
    name: str = Field(...)
    dosage: str = Field(...)
    frequency: str = Field(...)
    duration: str = Field(...)
    instructions: Optional[str] = None

class Prescription(MongoBaseModel):
    bookingId: PyObjectId = Field(...)
    patientId: PyObjectId = Field(...)
    doctorId: PyObjectId = Field(...)
    medications: List[Medication] = Field(default_factory=list)
    advice: Optional[str] = None
    nextFollowUp: Optional[datetime] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
