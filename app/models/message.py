from typing import Optional, List
from datetime import datetime, timezone
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class Attachment(MongoBaseModel):
    url: str
    fileType: Optional[str] = None
    name: Optional[str] = None

class Message(MongoBaseModel):
    sender: PyObjectId = Field(...)
    receiver: PyObjectId = Field(...)
    text: Optional[str] = None
    attachments: List[Attachment] = Field(default_factory=list)
    isRead: bool = False
    chatType: str = "DOCTOR_PATIENT"
    createdAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
ModelConfig = {
    "populate_by_name": True,
    "arbitrary_types_allowed": True
}
