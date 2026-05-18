from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date

class UserRegisterSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(..., pattern=r"^[0-9]{10,15}$")
    password: str = Field(..., min_length=6)
    gender: str = Field(..., description="male, female, or other")
    dob: date

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class VerifyOtpSchema(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)
