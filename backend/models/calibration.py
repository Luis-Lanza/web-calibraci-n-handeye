"""
Calibration-related models: CalibrationRun, RobotPose, and CameraPose.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..database import Base


class CalibrationStatus(str, enum.Enum):
    """Status of a calibration run."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"


class RobotPoseInputMethod(str, enum.Enum):
    """Method used to input robot poses."""
    CSV_IMPORT = "csv_import"
    MANUAL_ENTRY = "manual_entry"
    MIXED = "mixed"


class CalibrationRun(Base):
    """
    Model representing a complete calibration run.
    Contains the input poses, algorithm parameters, and calibration results.
    """
    __tablename__ = "calibration_runs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)  # Calibration name
    description = Column(String(1000), nullable=True)  # Optional description
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    algorithm_params_id = Column(Integer, ForeignKey("algorithm_parameters.id"), nullable=False)
    
    # ChArUco board parameters (provided by operator)
    charuco_squares_x = Column(Integer, nullable=False)  # Number of squares in X direction
    charuco_squares_y = Column(Integer, nullable=False)  # Number of squares in Y direction
    charuco_square_length = Column(Float, nullable=False)  # Square length in mm
    charuco_marker_length = Column(Float, nullable=False)  # ArUco marker length in mm
    charuco_dictionary = Column(String(50), default="DICT_4X4_50", nullable=False)  # ArUco dictionary type
    
    # Robot poses input method
    robot_poses_input_method = Column(SQLEnum(RobotPoseInputMethod), nullable=True)
    csv_filename = Column(String(255), nullable=True)  # Original CSV filename if imported
    
    # Results (stored as JSON for the 4x4 transformation matrix)
    transformation_matrix = Column(JSON, nullable=True)  # 4x4 homogeneous transformation matrix
    reprojection_error = Column(Float, nullable=True)
    status = Column(SQLEnum(CalibrationStatus), default=CalibrationStatus.PENDING, nullable=False)
    
    # Additional metadata
    notes = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="calibration_runs")
    robot_poses = relationship("RobotPose", back_populates="calibration_run", cascade="all, delete-orphan")
    camera_poses = relationship("CameraPose", back_populates="calibration_run", cascade="all, delete-orphan")
    algorithm_params = relationship("AlgorithmParameters", back_populates="calibration_runs")
    images = relationship("CalibrationImage", back_populates="calibration_run", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CalibrationRun(id={self.id}, status='{self.status.value}', error={self.reprojection_error})>"


class RobotPose(Base):
    """
    Model representing a single robot pose in a calibration sequence.
    Stores the rotation matrix and translation vector.
    """
    __tablename__ = "robot_poses"
    
    id = Column(Integer, primary_key=True, index=True)
    calibration_run_id = Column(Integer, ForeignKey("calibration_runs.id"), nullable=False, index=True)
    pose_index = Column(Integer, nullable=False)  # Order of the pose in the sequence
    
    # Original pose format (as provided by operator: X, Y, Z, Rx, Ry, Rz)
    x = Column(Float, nullable=False)  # X position (mm or m)
    y = Column(Float, nullable=False)  # Y position (mm or m)
    z = Column(Float, nullable=False)  # Z position (mm or m)
    rx = Column(Float, nullable=False)  # Rotation around X (degrees)
    ry = Column(Float, nullable=False)  # Rotation around Y (degrees)
    rz = Column(Float, nullable=False)  # Rotation around Z (degrees)
    
    # Input method
    input_method = Column(SQLEnum(RobotPoseInputMethod), nullable=False)
    
    # Computed transformation matrices (from X,Y,Z,Rx,Ry,Rz)
    rotation_matrix = Column(JSON, nullable=False)  # 3x3 rotation matrix (computed)
    translation_vector = Column(JSON, nullable=False)  # 3x1 translation vector (computed)
    
    # Relationship
    calibration_run = relationship("CalibrationRun", back_populates="robot_poses")
    
    def __repr__(self):
        return f"<RobotPose(id={self.id}, calibration_run_id={self.calibration_run_id}, index={self.pose_index})>"


class CameraPose(Base):
    """
    Model representing a single camera pose in a calibration sequence.
    Stores the rotation matrix and translation vector.
    Must correspond to a RobotPose with the same pose_index.
    """
    __tablename__ = "camera_poses"
    
    id = Column(Integer, primary_key=True, index=True)
    calibration_run_id = Column(Integer, ForeignKey("calibration_runs.id"), nullable=False, index=True)
    pose_index = Column(Integer, nullable=False)  # Must match corresponding RobotPose
    
    # Pose data (computed automatically from ChArUco image using OpenCV)
    rotation_matrix = Column(JSON, nullable=False)  # 3x3 rotation matrix (computed via solvePnP)
    translation_vector = Column(JSON, nullable=False)  # 3x1 translation vector (computed via solvePnP)
    
    # Computation metadata
    computed_automatically = Column(Boolean, default=True, nullable=False)  # Always True (computed by OpenCV)
    reprojection_error_individual = Column(Float, nullable=True)  # Reprojection error for this specific pose
    computed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    calibration_run = relationship("CalibrationRun", back_populates="camera_poses")
    
    def __repr__(self):
        return f"<CameraPose(id={self.id}, calibration_run_id={self.calibration_run_id}, index={self.pose_index})>"


class CalibrationImage(Base):
    """
    Model representing a ChArUco board image uploaded by the operator.
    Each image is processed to detect the ChArUco board and calculate camera pose.
    """
    __tablename__ = "calibration_images"
    
    id = Column(Integer, primary_key=True, index=True)
    calibration_run_id = Column(Integer, ForeignKey("calibration_runs.id"), nullable=False, index=True)
    pose_index = Column(Integer, nullable=False)  # Links to corresponding RobotPose
    
    # File metadata
    image_path = Column(String(500), nullable=False)  # Relative path to uploaded image
    original_filename = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    image_width = Column(Integer, nullable=True)  # Image width in pixels
    image_height = Column(Integer, nullable=True)  # Image height in pixels
    
    # ChArUco detection results (computed by OpenCV)
    charuco_detected = Column(Boolean, default=False, nullable=False)  # Was board detected?
    corners_detected = Column(Integer, nullable=True)  # Number of corners detected
    ids_detected = Column(Integer, nullable=True)  # Number of ArUco IDs detected
    
    # Link to computed camera pose
    camera_pose_id = Column(Integer, ForeignKey("camera_poses.id"), nullable=True)  # Set after processing
    
    # Relationship
    calibration_run = relationship("CalibrationRun", back_populates="images")
    camera_pose = relationship("CameraPose", foreign_keys=[camera_pose_id])
    
    def __repr__(self):
        return f"<CalibrationImage(id={self.id}, pose_index={self.pose_index}, detected={self.charuco_detected})>"
