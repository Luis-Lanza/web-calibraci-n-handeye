"""
Camera intrinsic parameters.
Provides default camera matrix and distortion coefficients for calibration.

In production, these should be obtained from a prior camera calibration process.
For development/testing, we use reasonable default values.
"""
import numpy as np


def get_default_camera_matrix(image_width: int = 1280, image_height: int = 720) -> np.ndarray:
    """
    Get default camera intrinsic matrix (3x3).
    
    The camera matrix format is:
        [fx  0  cx]
        [0  fy  cy]
        [0   0   1]
    
    Where:
    - fx, fy: Focal lengths in pixels
    - cx, cy: Principal point (image center)
    
    Args:
        image_width: Image width in pixels (default: 1280)
        image_height: Image height in pixels (default: 720)
        
    Returns:
        3x3 camera matrix
        
    Note:
        These are typical values for an industrial camera.
        For accurate calibration, perform camera calibration first.
    """
    # Typical focal length (in pixels) for industrial cameras
    # Approximately 1000-1500 for 1280x720
    fx = fy = 1000.0
    
    # Principal point at image center
    cx = image_width / 2.0
    cy = image_height / 2.0
    
    camera_matrix = np.array([
        [fx,  0, cx],
        [ 0, fy, cy],
        [ 0,  0,  1]
    ], dtype=np.float64)
    
    return camera_matrix


def get_default_distortion_coeffs() -> np.ndarray:
    """
    Get default distortion coefficients.
    
    Distortion coefficients format: (k1, k2, p1, p2[, k3])
    Where:
    - k1, k2, k3: Radial distortion coefficients
    - p1, p2: Tangential distortion coefficients
    
    Returns:
        Distortion coefficients array of shape (5,)
        
    Note:
        Assumes zero distortion (pinhole camera model).
        For accurate results, use actual camera calibration.
    """
    # Zero distortion (ideal pinhole camera)
    return np.zeros(5, dtype=np.float64)


def estimate_camera_matrix_from_fov(image_width: int, image_height: int, 
                                     fov_horizontal_deg: float = 60.0) -> np.ndarray:
    """
    Estimate camera matrix from field of view.
    
    Args:
        image_width: Image width in pixels
        image_height: Image height in pixels
        fov_horizontal_deg: Horizontal field of view in degrees
        
    Returns:
        3x3 camera matrix
        
    Example:
        >>> # For a camera with 60° horizontal FOV
        >>> K = estimate_camera_matrix_from_fov(1280, 720, 60.0)
    """
    # Convert FOV to radians
    fov_h_rad = np.deg2rad(fov_horizontal_deg)
    
    # Calculate focal length from FOV
    # fx = (image_width / 2) / tan(fov / 2)
    fx = (image_width / 2.0) / np.tan(fov_h_rad / 2.0)
    
    # Assume square pixels (fx = fy)
    fy = fx
    
    # Principal point at center
    cx = image_width / 2.0
    cy = image_height / 2.0
    
    camera_matrix = np.array([
        [fx,  0, cx],
        [ 0, fy, cy],
        [ 0,  0,  1]
    ], dtype=np.float64)
    
    return camera_matrix
