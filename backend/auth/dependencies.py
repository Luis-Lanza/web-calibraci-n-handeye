"""
FastAPI dependencies for authentication and authorization.
Provides reusable dependencies to protect endpoints and verify user roles.
"""
from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User, UserRole
from backend.schemas.token import TokenData
from backend.auth.security import decode_access_token

# OAuth2 scheme - this will look for the Authorization header with Bearer token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from the JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        The authenticated User object
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode the token
    token_data: TokenData = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure the current user is active.
    
    Args:
        current_user: The authenticated user
        
    Returns:
        The authenticated and active User object
        
    Raises:
        HTTPException 400: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def require_technician(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to require at least Technician role.
    Allows: Technician, Engineer, Supervisor
    
    Args:
        current_user: The authenticated and active user
        
    Returns:
        The user if authorized
        
    Raises:
        HTTPException 403: If user doesn't have required role
    """
    allowed_roles = [UserRole.TECHNICIAN, UserRole.ENGINEER, UserRole.SUPERVISOR]
    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


async def require_engineer(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to require Engineer role.
    Allows: Engineer only
    
    Args:
        current_user: The authenticated and active user
        
    Returns:
        The user if authorized
        
    Raises:
        HTTPException 403: If user doesn't have required role
    """
    if current_user.role != UserRole.ENGINEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Engineer role required"
        )
    return current_user


async def require_supervisor(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Dependency to require Supervisor role.
    Allows: Supervisor only
    
    Args:
        current_user: The authenticated and active user
        
    Returns:
        The user if authorized
        
    Raises:
        HTTPException 403: If user doesn't have required role
    """
    if current_user.role != UserRole.SUPERVISOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Supervisor role required"
        )
    return current_user


class RoleChecker:
    """
    Callable class to check if user has one of the allowed roles.
    Usage: Depends(RoleChecker([UserRole.ENGINEER, UserRole.TECHNICIAN]))
    """
    
    def __init__(self, allowed_roles: List[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: User = Depends(get_current_active_user)) -> User:
        """
        Check if current user has one of the allowed roles.
        
        Args:
            current_user: The authenticated and active user
            
        Returns:
            The user if authorized
            
        Raises:
            HTTPException 403: If user doesn't have required role
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires one of the following roles: {[role.value for role in self.allowed_roles]}"
            )
        return current_user
