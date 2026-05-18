from typing import Optional
from datetime import datetime
from pydantic import Field, model_validator
from app.models.base import MongoBaseModel, PyObjectId

class ProviderVerification(MongoBaseModel):
    providerType: str = Field(..., description="DOCTOR, NURSE")
    providerId: PyObjectId = Field(...)
    documentUrl: str = Field(..., max_length=255)
    status: str = Field(default="PENDING", description="PENDING, APPROVED, REJECTED")
    adminId: Optional[PyObjectId] = None
    remarks: Optional[str] = None
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_admin_id(self) -> 'ProviderVerification':
        if self.status != "PENDING" and not self.adminId:
            raise ValueError("adminId is required for APPROVED or REJECTED verifications")
        return self
