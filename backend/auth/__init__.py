"""
Authentication package.
Provides password hashing, JWT token management, and role-based access control.
"""
from .security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_technician,
    require_engineer,
    require_supervisor,
    RoleChecker
)

__all__ = [
    "get_password_hash",
    "verify_password",
    "create_access_token",
    "decode_access_token",
    "get_current_user",
    "get_current_active_user",
    "require_technician",
    "require_engineer",
    "require_supervisor",
    "RoleChecker"
]
