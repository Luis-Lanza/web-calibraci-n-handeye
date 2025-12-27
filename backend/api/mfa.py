from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from backend.database import get_db
from backend.models.user import User
from backend.auth.dependencies import get_current_active_user

router = APIRouter()

from pydantic import BaseModel

class MFAVerify(BaseModel):
    code: str

@router.post("/enable")
async def enable_mfa(
    verification: MFAVerify,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Enable MFA for the current user.
    Requires verifying the code sent to email first.
    """
    # Seguridad A07: Verificar código antes de activar MFA
    if not current_user.mfa_code or not current_user.mfa_code_expires_at:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No MFA code generated. Request one first."
        )
        
    if datetime.utcnow() > current_user.mfa_code_expires_at:
         raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA code expired"
        )
        
    if verification.code != current_user.mfa_code:
         raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code"
        )

    current_user.mfa_enabled = True
    current_user.mfa_code = None
    current_user.mfa_code_expires_at = None
    db.commit()
    return {"message": "MFA enabled successfully"}

@router.post("/generate")
async def generate_mfa_code(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Generate and send MFA code for setup."""
    from backend.services.email_service import EmailService
    from datetime import timedelta
    
    code = EmailService.generate_code()
    current_user.mfa_code = code
    current_user.mfa_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
    db.commit()
    
    EmailService.send_mfa_code(current_user.email, code)
    return {"message": "MFA code sent"}

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
