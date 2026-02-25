"""
Authentication-related Pydantic models
"""
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional


class UserLogin(BaseModel):
    """User login request"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)


class UserRegister(BaseModel):
    """User registration request"""
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: str = Field(..., min_length=6)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            normalized = value.strip()
            return normalized or None
        return value


class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(..., description="Expiration time (seconds)")


class TokenData(BaseModel):
    """Token data (decoded)"""
    username: Optional[str] = None
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    """User info response"""
    id: str
    username: str
    email: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[str] = None
