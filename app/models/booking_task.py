from typing import Optional
from datetime import datetime
from pydantic import Field
from app.models.base import MongoBaseModel, PyObjectId

class BookingTask(MongoBaseModel):
    bookingId: PyObjectId = Field(...)
    task: str = Field(..., max_length=100)
    isCompleted: bool = Field(default=False)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
