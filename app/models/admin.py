from typing import Optional
from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel

class Admin(MongoBaseModel):
    username: str = Field(..., unique=True, max_length=50)
    password: str
    name: Optional[str] = Field(default=None, max_length=50)
    role: str = Field(default="admin", description="super_admin, admin, moderator")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
