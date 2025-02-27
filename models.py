from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class Register(BaseModel):
    username: str = Field(min_length=3, max_length=20, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(min_length=6, max_length=50)
    email: str = EmailStr
    referral_code: Optional[str] = Field(None, min_length=6, max_length=10)


class ForgotPasswordRequest(BaseModel):
    username: str
    email: EmailStr
    

class ResetPasswordRequest(BaseModel):
    username: str
    email: EmailStr
    old_password: str
    new_password: str = Field(min_length=6, max_length=50)


class UserResponse(BaseModel):
    username: str
    email: str
