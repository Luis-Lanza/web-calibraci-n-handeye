from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend.models.user import User
from backend.auth.dependencies import get_current_active_user

router = APIRouter()

@router.post("/enable")
async def enable_mfa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Enable MFA for the current user."""
    current_user.mfa_enabled = True
    db.commit()
    return {"message": "MFA enabled successfully"}

@router.post("/disable")
async def disable_mfa(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Disable MFA for the current user."""
    current_user.mfa_enabled = False
    current_user.mfa_code = None
    current_user.mfa_code_expires_at = None
    db.commit()
    return {"message": "MFA disabled successfully"}

@router.get("/status")
async def get_mfa_status(
    current_user: User = Depends(get_current_active_user)
):
    """Get MFA status for current user."""
    return {"mfa_enabled": current_user.mfa_enabled}
