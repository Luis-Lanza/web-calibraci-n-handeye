"""
Pydantic schemas for User model.
Used for request/response validation in the API.
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from backend.models.user import UserRole


class UserBase(BaseModel):
    """Base User schema with common fields."""
    username: str
    email: EmailStr


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str
    role: UserRole = UserRole.TECHNICIAN


class UserResponse(UserBase):
    """Schema for User responses (excludes password)."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows ORM model to dict conversion


class UserInDB(UserBase):
    """Schema for User as stored in database (includes hashed password)."""
    id: int
    hashed_password: str
    role: UserRole
    is_active: bool
    
    class Config:
        from_attributes = True
