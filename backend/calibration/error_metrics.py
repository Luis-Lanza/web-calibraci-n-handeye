"""
Error metrics for hand-eye calibration.
Calculates reprojection and geometric errors.
"""
import numpy as np
from typing import List, Dict
from scipy.spatial.transform import Rotation as R


def calculate_reprojection_error(
    X: np.ndarray,
    robot_poses: List[np.ndarray],
    camera_poses: List[np.ndarray]
) -> Dict:
    """
    Calculate reprojection error for hand-eye calibration.
    
    For each pose pair, verifies: A * X ≈ X * B
    Error is the Frobenius norm of (A*X - X*B)
    
    Args:
        X: Hand-eye transformation (4x4 matrix)
        robot_poses: List of robot transformations A (4x4)
        camera_poses: List of camera transformations B (4x4)
        
    Returns:
        Dictionary with:
        - mean_error: Mean reprojection error
        - std_error: Standard deviation of errors
        - max_error: Maximum error
        - min_error: Minimum error
        - individual_errors: List of errors for each pose
        - rotation_errors_deg: List of rotation errors in degrees
        - translation_errors_mm: List of translation errors in mm
    """
    individual_errors = []
    rotation_errors = []
    translation_errors = []
    
    for A, B in zip(robot_poses, camera_poses):
        # Calculate: A*X and X*B
        AX = A @ X
        XB = X @ B
        
        # Frobenius norm of difference
        error = np.linalg.norm(AX - XB, 'fro')
        individual_errors.append(error)
        
        # Separate rotation and translation errors
        rot_error = calculate_rotation_error(AX[:3, :3], XB[:3, :3])
        trans_error = calculate_translation_error(AX[:3, 3], XB[:3, 3])
        
        rotation_errors.append(rot_error)
        translation_errors.append(trans_error)
    
    individual_errors = np.array(individual_errors)
    
    return {
        'mean_error': float(np.mean(individual_errors)),
        'std_error': float(np.std(individual_errors)),
        'max_error': float(np.max(individual_errors)),
        'min_error': float(np.min(individual_errors)),
        'individual_errors': individual_errors.tolist(),
        'rotation_errors_deg': rotation_errors,
        'translation_errors_mm': translation_errors,
        'mean_rotation_error_deg': float(np.mean(rotation_errors)),
        'mean_translation_error_mm': float(np.mean(translation_errors))
    }


def calculate_rotation_error(R1: np.ndarray, R2: np.ndarray) -> float:
    """
    Calculate rotation error between two rotation matrices.
    
    Error is measured as the angle of the relative rotation R1^T * R2.
    
    Args:
        R1: First rotation matrix (3x3)
        R2: Second rotation matrix (3x3)
        
    Returns:
        Rotation error in degrees
    """
    # Relative rotation
    R_rel = R1.T @ R2
    
    # Convert to scipy Rotation to get angle
    rot = R.from_matrix(R_rel)
    
    # Get rotation angle in degrees
    angle = rot.magnitude() * 180.0 / np.pi
    
    return float(angle)


def calculate_translation_error(t1: np.ndarray, t2: np.ndarray) -> float:
    """
    Calculate translation error as Euclidean distance.
    
    Args:
        t1: First translation vector (3,) or (3,1)
        t2: Second translation vector (3,) or (3,1)
        
    Returns:
        Translation error (same units as input, typically mm)
    """
    t1 = t1.ravel()
    t2 = t2.ravel()
    
    error = np.linalg.norm(t1 - t2)
    return float(error)


def calculate_pose_diversity(poses: List[np.ndarray]) -> Dict:
    """
    Calculate diversity metrics for a set of poses.
    
    Useful to ensure poses are sufficiently different for robust calibration.
    
    Args:
        poses: List of 4x4 transformation matrices
        
    Returns:
        Dictionary with:
        - mean_rotation_change_deg: Average rotation between consecutive poses
        - mean_translation_change_mm: Average translation between consecutive poses
        - max_rotation_change_deg: Maximum rotation change
        - max_translation_change_mm: Maximum translation change
    """
    if len(poses) < 2:
        return {
            'mean_rotation_change_deg': 0.0,
            'mean_translation_change_mm': 0.0,
            'max_rotation_change_deg': 0.0,
            'max_translation_change_mm': 0.0
        }
    
    rotation_changes = []
    translation_changes = []
    
    for i in range(len(poses) - 1):
        R1 = poses[i][:3, :3]
        R2 = poses[i + 1][:3, :3]
        t1 = poses[i][:3, 3]
        t2 = poses[i + 1][:3, 3]
        
        rot_change = calculate_rotation_error(R1, R2)
        trans_change = calculate_translation_error(t1, t2)
        
        rotation_changes.append(rot_change)
        translation_changes.append(trans_change)
    
    return {
        'mean_rotation_change_deg': float(np.mean(rotation_changes)),
        'mean_translation_change_mm': float(np.mean(translation_changes)),
        'max_rotation_change_deg': float(np.max(rotation_changes)),
        'max_translation_change_mm': float(np.max(translation_changes)),
        'min_rotation_change_deg': float(np.min(rotation_changes)),
        'min_translation_change_mm': float(np.min(translation_changes))
    }
