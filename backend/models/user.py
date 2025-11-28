"""
User model for authentication and role-based access control.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class UserRole(str, enum.Enum):
    """Enumeration of user roles in the system."""
    TECHNICIAN = "technician"
    ENGINEER = "engineer"
    SUPERVISOR = "supervisor"


class User(Base):
    """
    User model for the Hand-Eye Calibration System.
    
    Roles:
    - technician: Can load data, execute calibrations, and view/export results
    - engineer: All technician permissions + configure algorithm parameters
    - supervisor: Read-only access to history and reports
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.TECHNICIAN, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # MFA fields
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    mfa_code = Column(String(6), nullable=True)  # Temporary 6-digit code
    mfa_code_expires_at = Column(DateTime, nullable=True)
    
    # Relationships
    calibration_runs = relationship("CalibrationRun", back_populates="user", cascade="all, delete-orphan")
    algorithm_parameters = relationship("AlgorithmParameters", back_populates="created_by", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}', role='{self.role.value}')>"
