from typing import Optional, Any
from datetime import datetime
from pydantic import Field, BaseModel
from app.models.base import MongoBaseModel, PyObjectId

class Banner(MongoBaseModel):
    title: Optional[str] = None
    imageUrl: str = Field(...)
    link: Optional[str] = None
    target: str = Field(default="ALL", description="USER, DOCTOR, NURSE, ALL")
    active: bool = Field(default=True)
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

class SystemConfig(MongoBaseModel):
    key: str = Field(...)
    value: Any = Field(...)
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)

class Announcement(MongoBaseModel):
    title: str = Field(...)
    body: str = Field(...)
    target: str = Field(default="ALL", description="USER, DOCTOR, NURSE, ALL")
    active: bool = Field(default=True)
    expiresAt: Optional[datetime] = None
    createdAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updatedAt: Optional[datetime] = Field(default_factory=datetime.utcnow)
