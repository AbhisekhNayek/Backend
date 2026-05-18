from pydantic import BaseModel, Field
from typing import Optional, List

class DoctorLoginSchema(BaseModel):
    username: str
    password: str

class DoctorFeesSchema(BaseModel):
    video: Optional[float] = Field(default=None, ge=0)
    clinic: Optional[float] = Field(default=None, ge=0)

class DoctorUpdateProfileSchema(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = Field(default=None, max_length=500)
    specialization: Optional[str] = None
    qualifications: Optional[List[str]] = None
    experience: Optional[int] = Field(default=None, ge=0)
    languages: Optional[List[str]] = None
    fees: Optional[DoctorFeesSchema] = None
