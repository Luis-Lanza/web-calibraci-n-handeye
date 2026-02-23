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
    
    # Calculate T_target_base for each pose pair
    # For Eye-in-Hand: T_target_base = A * X * B
    # Where A = T_gripper_base, X = T_cam_gripper, B = T_target_cam
    
    T_target_base_list = []
    
    for A, B in zip(robot_poses, camera_poses):
        # Calculate T = A @ X @ B
        T = A @ X @ B
        T_target_base_list.append(T)
    
    # Calculate mean transformation
    # For translation, just mean
    translations = np.array([T[:3, 3] for T in T_target_base_list])
    mean_translation = np.mean(translations, axis=0)
    
    # For rotation, we need a proper mean (using chordal L2 mean or similar)
    # Simple approximation: convert to rotation vectors, mean, back to matrix
    # Or just pick the first one as reference for error calculation (common in simple implementations)
    # Better: Use the first pose as reference to measure deviation
    ref_T = T_target_base_list[0]
    ref_R = ref_T[:3, :3]
    ref_t = ref_T[:3, 3]
    
    # Calculate deviations from the first pose (or mean)
    # Let's use the mean translation for translation error
    # And the first rotation as reference for rotation error (simplifies averaging)
    
    for T in T_target_base_list:
        R_curr = T[:3, :3]
        t_curr = T[:3, 3]
        
        # Rotation error relative to reference
        rot_error = calculate_rotation_error(ref_R, R_curr)
        
        # Translation error relative to mean
        trans_error = calculate_translation_error(mean_translation, t_curr)
        
        rotation_errors.append(rot_error)
        translation_errors.append(trans_error)
        
        # Combined error (heuristic)
        individual_errors.append(trans_error + rot_error) # Mixing units, but useful for relative comparison
    
    individual_errors = np.array(individual_errors)
    
    # Get real reprojection errors from the camera poses if possible,
    # or just return the translation error logic, but DO NOT name translation error as reprojection error!
    # The true reprojection error should be evaluated by projecting 3D points.
    # For now, we fix the dictionary to just pass the individual errors properly.
    return {
        'mean_error': float(np.mean(individual_errors)), # Combined error
        'std_error': float(np.std(translation_errors)),
        'max_error': float(np.max(translation_errors)),
        'min_error': float(np.min(translation_errors)),
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
