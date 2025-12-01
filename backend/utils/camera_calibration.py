"""
Utility functions for parsing camera calibration files.
Supports OpenCV YAML and JSON formats.
"""
import json
import yaml
import numpy as np
from typing import Dict, Optional, Tuple


def parse_opencv_yaml(file_content: str) -> Dict[str, any]:
    """
    Parse OpenCV YAML camera calibration file.
    
    Expected format:
    ```yaml
    %YAML:1.0
    camera_matrix: !!opencv-matrix
       rows: 3
       cols: 3
       dt: d
       data: [ fx, 0, cx, 0, fy, cy, 0, 0, 1 ]
    distortion_coefficients: !!opencv-matrix
       rows: 1
       cols: 5
       dt: d
       data: [ k1, k2, p1, p2, k3 ]
    ```
    
    Args:
        file_content: YAML file content as string
        
    Returns:
        Dictionary with keys:
        - fx, fy, cx, cy: Intrinsic matrix parameters
        - k1, k2, p1, p2, k3: Distortion coefficients
        
    Raises:
        ValueError: If file format is invalid or required keys are missing
    """
    try:
        # Parse YAML
        data = yaml.safe_load(file_content)
        
        # Extract camera matrix
        if 'camera_matrix' not in data:
            raise ValueError("Missing 'camera_matrix' in YAML file")
        
        camera_matrix_data = data['camera_matrix']['data']
        if len(camera_matrix_data) != 9:
            raise ValueError(f"Expected 9 values in camera_matrix, got {len(camera_matrix_data)}")
        
        # Extract intrinsic parameters (fx, fy, cx, cy from 3x3 matrix)
        fx = camera_matrix_data[0]
        fy = camera_matrix_data[4]
        cx = camera_matrix_data[2]
        cy = camera_matrix_data[5]
        
        # Extract distortion coefficients
        if 'distortion_coefficients' not in data:
            raise ValueError("Missing 'distortion_coefficients' in YAML file")
        
        dist_coeffs = data['distortion_coefficients']['data']
        if len(dist_coeffs) < 5:
            raise ValueError(f"Expected at least 5 distortion coefficients, got {len(dist_coeffs)}")
        
        k1, k2, p1, p2, k3 = dist_coeffs[:5]
        
        return {
            'fx': float(fx),
            'fy': float(fy),
            'cx': float(cx),
            'cy': float(cy),
            'k1': float(k1),
            'k2': float(k2),
            'p1': float(p1),
            'p2': float(p2),
            'k3': float(k3)
        }
        
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML format: {e}")
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Invalid camera calibration file structure: {e}")


def parse_opencv_json(file_content: str) -> Dict[str, any]:
    """
    Parse OpenCV JSON camera calibration file.
    
    Expected format:
    ```json
    {
      "camera_matrix": [[fx, 0, cx], [0, fy, cy], [0, 0, 1]],
      "distortion_coefficients": [k1, k2, p1, p2, k3]
    }
    ```
    
    Args:
        file_content: JSON file content as string
        
    Returns:
        Dictionary with keys:
        - fx, fy, cx, cy: Intrinsic matrix parameters
        - k1, k2, p1, p2, k3: Distortion coefficients
        
    Raises:
        ValueError: If file format is invalid or required keys are missing
    """
    try:
        data = json.loads(file_content)
        
        # Extract camera matrix
        if 'camera_matrix' not in data:
            raise ValueError("Missing 'camera_matrix' in JSON file")
        
        camera_matrix = data['camera_matrix']
        if not isinstance(camera_matrix, list) or len(camera_matrix) != 3:
            raise ValueError("camera_matrix must be a 3x3 matrix")
        
        fx = camera_matrix[0][0]
        fy = camera_matrix[1][1]
        cx = camera_matrix[0][2]
        cy = camera_matrix[1][2]
        
        # Extract distortion coefficients
        if 'distortion_coefficients' not in data:
            raise ValueError("Missing 'distortion_coefficients' in JSON file")
        
        dist_coeffs = data['distortion_coefficients']
        if len(dist_coeffs) < 5:
            raise ValueError(f"Expected at least 5 distortion coefficients, got {len(dist_coeffs)}")
        
        k1, k2, p1, p2, k3 = dist_coeffs[:5]
        
        return {
            'fx': float(fx),
            'fy': float(fy),
            'cx': float(cx),
            'cy': float(cy),
            'k1': float(k1),
            'k2': float(k2),
            'p1': float(p1),
            'p2': float(p2),
            'k3': float(k3)
        }
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}")
    except (KeyError, IndexError, TypeError) as e:
        raise ValueError(f"Invalid camera calibration file structure: {e}")


def validate_camera_params(params: Dict[str, float]) -> Tuple[bool, str]:
    """
    Validate camera calibration parameters.
    
    Args:
        params: Dictionary with camera parameters
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_keys = ['fx', 'fy', 'cx', 'cy', 'k1', 'k2', 'p1', 'p2', 'k3']
    
    # Check all keys present
    missing_keys = [k for k in required_keys if k not in params]
    if missing_keys:
        return False, f"Missing parameters: {', '.join(missing_keys)}"
    
    # Validate ranges
    if params['fx'] <= 0 or params['fy'] <= 0:
        return False, "Focal lengths (fx, fy) must be positive"
    
    if params['cx'] < 0 or params['cy'] < 0:
        return False, "Principal point (cx, cy) must be non-negative"
    
    # Distortion coefficients can be any value (including negative)
    # but should be reasonable (typically < 1.0 in absolute value)
    for key in ['k1', 'k2', 'k3']:
        if abs(params[key]) > 5.0:
            return False, f"Distortion coefficient {key}={params[key]} seems unreasonably large (|value| > 5.0)"
    
    for key in ['p1', 'p2']:
        if abs(params[key]) > 5.0:
            return False, f"Distortion coefficient {key}={params[key]} seems unreasonably large (|value| > 5.0)"
    
    return True, ""


def params_to_opencv_format(params: Dict[str, float]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert parameter dictionary to OpenCV camera matrix and distortion coefficients.
    
    Args:
        params: Dictionary with camera parameters
        
    Returns:
        Tuple of (camera_matrix, dist_coeffs) as numpy arrays
    """
    camera_matrix = np.array([
        [params['fx'], 0, params['cx']],
        [0, params['fy'], params['cy']],
        [0, 0, 1]
    ], dtype=np.float64)
    
    dist_coeffs = np.array([
        params['k1'],
        params['k2'],
        params['p1'],
        params['p2'],
        params['k3']
    ], dtype=np.float64)
    
    return camera_matrix, dist_coeffs
