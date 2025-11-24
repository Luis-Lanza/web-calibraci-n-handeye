"""
Tsai-Lenz Hand-Eye Calibration Algorithm.
Solves the equation AX = XB to find the hand-eye transformation X.

Where:
- A: Robot end-effector transformations (base → end-effector)
- B: Camera target transformations (target → camera)  
- X: Hand-eye transformation (end-effector → camera) - WHAT WE'RE SOLVING FOR
"""
import cv2
import numpy as np
from typing import List, Dict
from backend.calibration.transformations import matrix_to_rotation_translation


def solve_hand_eye_opencv(
    robot_poses: List[np.ndarray],
    camera_poses: List[np.ndarray],
    method: int = cv2.CALIB_HAND_EYE_TSAI
) -> Dict:
    """
    Solve hand-eye calibration using OpenCV's implementation.
    
    Args:
        robot_poses: List of 4x4 transformation matrices (A)
        camera_poses: List of 4x4 transformation matrices (B)
        method: Calibration method (default: CALIB_HAND_EYE_TSAI)
            Options:
            - cv2.CALIB_HAND_EYE_TSAI (Tsai-Lenz)
            - cv2.CALIB_HAND_EYE_PARK (Park-Martin)
            - cv2.CALIB_HAND_EYE_HORAUD (Horaud)
            - cv2.CALIB_HAND_EYE_ANDREFF (Andreff)
            - cv2.CALIB_HAND_EYE_DANIILIDIS (Daniilidis)
            
    Returns:
        Dictionary with:
        - X: Hand-eye transformation (4x4 matrix)
        - R_cam2gripper: Rotation part (3x3)
        - t_cam2gripper: Translation part (3x1)
        - num_poses_used: Number of pose pairs used
        - method_name: Name of method used
    """
    # Extract rotations and translations
    R_gripper2base = []
    t_gripper2base = []
    R_target2cam = []
    t_target2cam = []
    
    for A in robot_poses:
        R, t = matrix_to_rotation_translation(A)
        R_gripper2base.append(R)
        t_gripper2base.append(t.reshape(3, 1))
    
    for B in camera_poses:
        R, t = matrix_to_rotation_translation(B)
        R_target2cam.append(R)
        t_target2cam.append(t.reshape(3, 1))
    
    # Call OpenCV's calibrateHandEye
    R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(
        R_gripper2base,
        t_gripper2base,
        R_target2cam,
        t_target2cam,
        method=method
    )
    
    # Build homogeneous transformation matrix
    X = np.eye(4)
    X[:3, :3] = R_cam2gripper
    X[:3, 3] = t_cam2gripper.ravel()
    
    # Get method name
    method_names = {
        cv2.CALIB_HAND_EYE_TSAI: "Tsai-Lenz",
        cv2.CALIB_HAND_EYE_PARK: "Park-Martin",
        cv2.CALIB_HAND_EYE_HORAUD: "Horaud",
        cv2.CALIB_HAND_EYE_ANDREFF: "Andreff",
        cv2.CALIB_HAND_EYE_DANIILIDIS: "Daniilidis"
    }
    
    return {
        'X': X,
        'R_cam2gripper': R_cam2gripper,
        't_cam2gripper': t_cam2gripper,
        'num_poses_used': len(robot_poses),
        'method_name': method_names.get(method, "Unknown")
    }


def solve_hand_eye_tsai_lenz(
    robot_poses: List[np.ndarray],
    camera_poses: List[np.ndarray]
) -> Dict:
    """
    Solve hand-eye calibration using Tsai-Lenz method (wrapper).
    
    This is a convenience function that calls solve_hand_eye_opencv
    with the Tsai-Lenz method.
    
    Args:
        robot_poses: List of 4x4 transformation matrices (A)
        camera_poses: List of 4x4 transformation matrices (B)
        
    Returns:
        Dictionary with calibration results
    """
    return solve_hand_eye_opencv(
        robot_poses,
        camera_poses,
        method=cv2.CALIB_HAND_EYE_TSAI
    )


def validate_pose_pairs(
    robot_poses: List[np.ndarray],
    camera_poses: List[np.ndarray],
    min_poses: int = 3
) -> Dict:
    """
    Validate that pose pairs are suitable for calibration.
    
    Args:
        robot_poses: List of robot transformation matrices
        camera_poses: List of camera transformation matrices
        min_poses: Minimum number of poses required
        
    Returns:
        Dictionary with:
        - valid: bool (whether validation passed)
        - num_poses: Number of poses
        - errors: List of error messages (if any)
        - warnings: List of warning messages (if any)
    """
    errors = []
    warnings = []
    
    # Check equal length
    if len(robot_poses) != len(camera_poses):
        errors.append(
            f"Mismatch in number of poses: {len(robot_poses)} robot poses "
            f"vs {len(camera_poses)} camera poses"
        )
    
    num_poses = min(len(robot_poses), len(camera_poses))
    
    # Check minimum number of poses
    if num_poses < min_poses:
        errors.append(
            f"Insufficient poses: need at least {min_poses}, got {num_poses}"
        )
    
    # Check for NaN or Inf values
    for i, pose in enumerate(robot_poses):
        if np.any(np.isnan(pose)) or np.any(np.isinf(pose)):
            errors.append(f"Robot pose {i} contains NaN or Inf values")
    
    for i, pose in enumerate(camera_poses):
        if np.any(np.isnan(pose)) or np.any(np.isinf(pose)):
            errors.append(f"Camera pose {i} contains NaN or Inf values")
    
    # Check for duplicate poses (robot)
    for i in range(len(robot_poses)):
        for j in range(i + 1, len(robot_poses)):
            if np.allclose(robot_poses[i], robot_poses[j], atol=1e-6):
                warnings.append(
                    f"Robot poses {i} and {j} are very similar or identical"
                )
                break
    
    # Warn if too few poses
    if 3 <= num_poses < 8:
        warnings.append(
            f"Only {num_poses} poses provided. Recommend 8-15 for robust calibration."
        )
    
    return {
        'valid': len(errors) == 0,
        'num_poses': num_poses,
        'errors': errors,
        'warnings': warnings
    }
