from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel

class Message(MongoBaseModel):
    role: str = Field(..., description="user or model or system")
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AISession(MongoBaseModel):
    userId: str
    sessionType: str = Field(..., description="GENERAL_CHAT, LAB_ANALYST, or PINK_MODE")
    history: List[Message] = Field(default_factory=list)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
