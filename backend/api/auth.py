"""
Authentication API endpoints.
Provides login and user info endpoints.
"""
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import UserResponse
from backend.schemas.token import Token
from backend.auth.security import verify_password, create_access_token, get_password_hash
from backend.auth.dependencies import get_current_active_user
from backend.config import settings

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login endpoint.
    
    **Returns**:
    - access_token: JWT token
    - token_type: "bearer"
    
    **Errors**:
    - 401: Incorrect username or password
    """
    # Get user from database
    user = db.query(User).filter(User.username == form_data.username).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    # MFA Logic
    if user.mfa_enabled:
        # Check if MFA code is provided
        if not form_data.client_secret: # We use client_secret field for MFA code
            # Generate and send code
            from backend.services.email_service import EmailService
            from backend.services.email_service import EmailService
            
            code = EmailService.generate_code()
            user.mfa_code = code
            user.mfa_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
            db.commit()
            
            EmailService.send_mfa_code(user.email, code)
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="MFA_REQUIRED",
                headers={"WWW-Authenticate": "Bearer"},
            )
        else:
            # Verify code
            if not user.mfa_code or not user.mfa_code_expires_at:
                 raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code",
                )
                
            if datetime.utcnow() > user.mfa_code_expires_at:
                 raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="MFA code expired",
                )
                
            if form_data.client_secret != user.mfa_code:
                 raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code",
                )
                
            # Clear code after successful use
            user.mfa_code = None
            user.mfa_code_expires_at = None
            db.commit()
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    **Requires**: Authentication
    
    **Returns**: Current user details (excluding password)
    """
    return current_user
