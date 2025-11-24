"""
Algorithm parameters model for configuring calibration algorithms.
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from ..database import Base


class AlgorithmParameters(Base):
    """
    Model for storing algorithm configuration parameters.
    Engineers can create and modify these parameters.
    """
    __tablename__ = "algorithm_parameters"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    algorithm_type = Column(String(50), default="tsai_lenz", nullable=False)
    
    # Algorithm-specific parameters
    tolerance = Column(Float, default=1e-6, nullable=False)
    max_iterations = Column(Integer, default=100, nullable=False)
    optimization_method = Column(String(50), default="svd", nullable=False)  # e.g., "svd", "iterative"
    
    # Metadata
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    description = Column(String(500), nullable=True)
    
    # Relationships
    created_by = relationship("User", back_populates="algorithm_parameters")
    calibration_runs = relationship("CalibrationRun", back_populates="algorithm_params")
    
    def __repr__(self):
        return f"<AlgorithmParameters(name='{self.name}', type='{self.algorithm_type}', default={self.is_default})>"
