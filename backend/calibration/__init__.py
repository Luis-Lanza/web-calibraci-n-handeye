"""
Calibration package.
Provides ChArUco detection, pose estimation, and hand-eye calibration algorithms.
"""
from .transformations import (
    euler_to_rotation_matrix,
    rotation_matrix_to_euler,
    create_homogeneous_matrix,
    matrix_to_rotation_translation,
    pose_euler_to_matrix,
    matrix_to_pose_euler,
    rodrigues_to_rotation_matrix,
    rotation_matrix_to_rodrigues,
    invert_homogeneous_matrix
)
from .charuco_detector import ChArUcoDetector
from .camera_params import (
    get_default_camera_matrix,
    get_default_distortion_coeffs,
    estimate_camera_matrix_from_fov
)
from .tsai_lenz import (
    solve_hand_eye_tsai_lenz,
    solve_hand_eye_opencv,
    validate_pose_pairs
)
from .error_metrics import (
    calculate_reprojection_error,
    calculate_rotation_error,
    calculate_translation_error,
    calculate_pose_diversity
)
from .calibration_service import CalibrationService

__all__ = [
    # Transformations
    "euler_to_rotation_matrix",
    "rotation_matrix_to_euler",
    "create_homogeneous_matrix",
    "matrix_to_rotation_translation",
    "pose_euler_to_matrix",
    "matrix_to_pose_euler",
    "rodrigues_to_rotation_matrix",
    "rotation_matrix_to_rodrigues",
    "invert_homogeneous_matrix",
    # ChArUco detection
    "ChArUcoDetector",
    # Camera parameters
    "get_default_camera_matrix",
    "get_default_distortion_coeffs",
    "estimate_camera_matrix_from_fov",
    # Calibration algorithms
    "solve_hand_eye_tsai_lenz",
    "solve_hand_eye_opencv",
    "validate_pose_pairs",
    # Error metrics
    "calculate_reprojection_error",
    "calculate_rotation_error",
    "calculate_translation_error",
    "calculate_pose_diversity",
    # Calibration service
    "CalibrationService"
]
