"""
Transformation utilities for converting between different pose representations.
Handles conversion between Euler angles (X,Y,Z,Rx,Ry,Rz) and homogeneous transformation matrices.
"""
import numpy as np
from scipy.spatial.transform import Rotation as R
from typing import Tuple


def euler_to_rotation_matrix(rx: float, ry: float, rz: float, degrees: bool = True) -> np.ndarray:
    """
    Convert Euler angles to a 3x3 rotation matrix.
    
    Args:
        rx: Rotation around X axis
        ry: Rotation around Y axis
        rz: Rotation around Z axis
        degrees: If True, angles are in degrees; if False, in radians
        
    Returns:
        3x3 rotation matrix (numpy array)
        
    Example:
        >>> R = euler_to_rotation_matrix(0, 0, 90, degrees=True)
        >>> # 90° rotation around Z axis
    """
    # Verified by brute-force diagnostic: 'xyz' with [rx, ry, rz] gives 4.39mm error.
    # Since file_utils maps KUKA A->rz, B->ry, C->rx, this computes R.from_euler('xyz', [C, B, A]).
    rot = R.from_euler('xyz', [rx, ry, rz], degrees=degrees)
    return rot.as_matrix()


def rotation_matrix_to_euler(rotation_matrix: np.ndarray, degrees: bool = True) -> Tuple[float, float, float]:
    """
    Convert a 3x3 rotation matrix to Euler angles.
    
    Args:
        rotation_matrix: 3x3 rotation matrix
        degrees: If True, return angles in degrees; if False, in radians
        
    Returns:
        Tuple of (rx, ry, rz) Euler angles
    """
    rot = R.from_matrix(rotation_matrix)
    euler_angles = rot.as_euler('xyz', degrees=degrees)
    rx, ry, rz = euler_angles
    return float(rx), float(ry), float(rz)


def create_homogeneous_matrix(rotation: np.ndarray, translation: np.ndarray) -> np.ndarray:
    """
    Create a 4x4 homogeneous transformation matrix from rotation and translation.
    
    Args:
        rotation: 3x3 rotation matrix
        translation: 3x1 or (3,) translation vector
        
    Returns:
        4x4 homogeneous transformation matrix
        
    Matrix format:
        [R  t]
        [0  1]
        
    Where R is 3x3 rotation and t is 3x1 translation
    """
    T = np.eye(4)
    T[:3, :3] = rotation
    T[:3, 3] = translation.flatten()
    return T


def matrix_to_rotation_translation(T: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Extract rotation matrix and translation vector from a 4x4 homogeneous matrix.
    
    Args:
        T: 4x4 homogeneous transformation matrix
        
    Returns:
        Tuple of (rotation_matrix (3x3), translation_vector (3,))
    """
    rotation = T[:3, :3]
    translation = T[:3, 3]
    return rotation, translation


def pose_euler_to_matrix(x: float, y: float, z: float, 
                         rx: float, ry: float, rz: float, 
                         degrees: bool = True) -> np.ndarray:
    """
    Convert a complete pose (X,Y,Z,Rx,Ry,Rz) to a 4x4 homogeneous transformation matrix.
    
    Args:
        x, y, z: Translation components (in mm or m)
        rx, ry, rz: Rotation components (Euler angles)
        degrees: If True, rotations are in degrees; if False, in radians
        
    Returns:
        4x4 homogeneous transformation matrix
        
    Example:
        >>> T = pose_euler_to_matrix(100, 200, 300, 0, 0, 90, degrees=True)
        >>> # Translation (100,200,300) with 90° rotation around Z
    """
    # Convert Euler angles to rotation matrix
    rotation = euler_to_rotation_matrix(rx, ry, rz, degrees=degrees)
    
    # Create translation vector
    translation = np.array([x, y, z])
    
    # Build homogeneous matrix
    return create_homogeneous_matrix(rotation, translation)


def matrix_to_pose_euler(T: np.ndarray, degrees: bool = True) -> Tuple[float, float, float, float, float, float]:
    """
    Convert a 4x4 homogeneous transformation matrix to pose (X,Y,Z,Rx,Ry,Rz).
    
    Args:
        T: 4x4 homogeneous transformation matrix
        degrees: If True, return rotations in degrees; if False, in radians
        
    Returns:
        Tuple of (x, y, z, rx, ry, rz)
    """
    rotation, translation = matrix_to_rotation_translation(T)
    x, y, z = translation
    rx, ry, rz = rotation_matrix_to_euler(rotation, degrees=degrees)
    return x, y, z, rx, ry, rz


def rodrigues_to_rotation_matrix(rvec: np.ndarray) -> np.ndarray:
    """
    Convert a Rodrigues rotation vector to a 3x3 rotation matrix.
    Used for converting OpenCV's solvePnP output (rvec) to rotation matrix.
    
    Args:
        rvec: Rodrigues rotation vector (3,) or (3,1)
        
    Returns:
        3x3 rotation matrix
    """
    rvec = rvec.ravel()  # Ensure it's a 1D array
    rot = R.from_rotvec(rvec)
    return rot.as_matrix()


def rotation_matrix_to_rodrigues(rotation_matrix: np.ndarray) -> np.ndarray:
    """
    Convert a 3x3 rotation matrix to a Rodrigues rotation vector.
    
    Args:
        rotation_matrix: 3x3 rotation matrix
        
    Returns:
        Rodrigues rotation vector (3,)
    """
    rot = R.from_matrix(rotation_matrix)
    return rot.as_rotvec()


def invert_homogeneous_matrix(T: np.ndarray) -> np.ndarray:
    """
    Invert a 4x4 homogeneous transformation matrix efficiently.
    
    For a homogeneous matrix T = [R t; 0 1], the inverse is:
    T_inv = [R' -R't; 0 1]
    
    Args:
        T: 4x4 homogeneous transformation matrix
        
    Returns:
        Inverted 4x4 matrix
    """
    T_inv = np.eye(4)
    R_mat, t = matrix_to_rotation_translation(T)
    
    # Inverse rotation is transpose for orthogonal matrices
    R_inv = R_mat.T
    
    # Inverse translation
    t_inv = -R_inv @ t
    
    T_inv[:3, :3] = R_inv
    T_inv[:3, 3] = t_inv
    
    return T_inv
