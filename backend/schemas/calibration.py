"""
Pydantic schemas for calibration-related API endpoints.
Defines request/response models for calibration runs, robot poses, and execution results.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from backend.models.calibration import CalibrationStatus, RobotPoseInputMethod


class CalibrationRunCreate(BaseModel):
    """Schema for creating a new calibration run"""
    name: str = Field(..., min_length=1, max_length=200, description="Calibration name")
    description: Optional[str] = Field(None, max_length=1000, description="Optional description")
    charuco_squares_x: int = Field(7, ge=3, le=20, description="ChArUco squares in X direction")
    charuco_squares_y: int = Field(5, ge=3, le=20, description="ChArUco squares in Y direction")
    charuco_square_length: float = Field(100.0, gt=0, description="Square length in mm")
    charuco_marker_length: float = Field(75.0, gt=0, description="Marker length in mm")
    charuco_dictionary: str = Field("DICT_5X5_100", description="ArUco dictionary name")
    
    @validator('charuco_marker_length')
    def marker_smaller_than_square(cls, v, values):
        if 'charuco_square_length' in values and v >= values['charuco_square_length']:
            raise ValueError('Marker length must be smaller than square length')
        return v


class CalibrationRunResponse(BaseModel):
    """Schema for calibration run response"""
    id: int
    name: str
    description: Optional[str]
    status: str
    charuco_squares_x: int
    charuco_squares_y: int
    charuco_square_length: float
    charuco_marker_length: float
    charuco_dictionary: str
    transformation_matrix: Optional[List[List[float]]]
    reprojection_error: Optional[float]
    robot_poses_input_method: Optional[str]
    csv_filename: Optional[str]
    created_at: datetime
    user_id: int
    algorithm_params_id: int
    
    class Config:
        from_attributes = True  # For Pydantic v2 (was orm_mode in v1)


class RobotPoseCreate(BaseModel):
    """Schema for adding a robot pose"""
    pose_index: int = Field(..., ge=1, description="Pose index (1-based)")
    x: float = Field(..., description="X position in mm")
    y: float = Field(..., description="Y position in mm")
    z: float = Field(..., description="Z position in mm")
    rx: float = Field(..., description="Rotation around X axis in degrees")
    ry: float = Field(..., description="Rotation around Y axis in degrees")
    rz: float = Field(..., description="Rotation around Z axis in degrees")


class RobotPoseResponse(BaseModel):
    """Schema for robot pose response"""
    id: int
    calibration_run_id: int
    pose_index: int
    x: float
    y: float
    z: float
    rx: float
    ry: float
    rz: float
    input_method: str
    
    class Config:
        from_attributes = True


class CalibrationImageResponse(BaseModel):
    """Schema for calibration image response"""
    id: int
    calibration_run_id: int
    pose_index: int
    image_path: str
    original_filename: str
    uploaded_at: datetime
    file_size_bytes: int
    image_width: Optional[int]
    image_height: Optional[int]
    charuco_detected: Optional[bool]
    corners_detected: Optional[int]
    ids_detected: Optional[int]
    camera_pose_id: Optional[int]
    
    class Config:
        from_attributes = True


class CameraPoseResponse(BaseModel):
    """Schema for camera pose response"""
    id: int
    calibration_run_id: int
    pose_index: int
    rotation_matrix: List[List[float]]
    translation_vector: List[float]
    computed_automatically: bool
    reprojection_error_individual: Optional[float]
    computed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class CalibrationExecuteResponse(BaseModel):
    """Schema for calibration execution response"""
    success: bool
    calibration_id: int
    transformation_matrix: Optional[List[List[float]]]
    reprojection_error: Optional[float]
    rotation_error_deg: Optional[float]
    translation_error_mm: Optional[float]
    poses_processed: int
    poses_valid: int
    method: Optional[str] = None
    error_message: Optional[str] = None


class CSVImportResponse(BaseModel):
    """Schema for CSV import response"""
    success: bool
    poses_imported: int
    filename: str
    errors: List[str] = []


class ImageUploadResponse(BaseModel):
    """Schema for image upload response"""
    success: bool
    images_uploaded: int
    filenames: List[str]
    errors: List[str] = []
