"""
Pydantic schemas for User entity
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base User schema"""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    role: Optional[str] = Field(None, max_length=50)


class UserCreate(UserBase):
    """Schema for creating a new user"""
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    """Schema for updating a user"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    role: Optional[str] = Field(None, max_length=50)
    password: Optional[str] = Field(None, min_length=6)
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """Schema for user in database"""
    id: str
    password_hash: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class User(UserBase):
    """Schema for user response (without password)"""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: str
    email: str


class LoginResponse(BaseModel):
    """Login response with token and user info"""
    access_token: str
    token_type: str = "bearer"
    user: User
