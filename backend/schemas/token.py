"""
Pydantic schemas for authentication tokens.
"""
from pydantic import BaseModel
from typing import Optional
from backend.models.user import UserRole


class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for decoded token data."""
    username: Optional[str] = None
    role: Optional[UserRole] = None
