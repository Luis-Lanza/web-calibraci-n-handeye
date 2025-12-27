"""
Pydantic schemas for User model.
Used for request/response validation in the API.
"""
from pydantic import BaseModel, EmailStr, field_validator
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

    @field_validator('password')
    def validate_password(cls, v):
        # Seguridad A07: Política de contraseñas fuertes
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(char in "!@#$%^&*()_+-=[]{}|;:,.<>?" for char in v):
            raise ValueError('Password must contain at least one special character')
        return v


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
