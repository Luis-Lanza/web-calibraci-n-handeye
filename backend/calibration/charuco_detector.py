"""
ChArUco board detection and camera pose estimation using OpenCV.
Provides a class to detect ChArUco boards in images and estimate camera poses.
"""
import cv2
import numpy as np
from typing import Optional, Dict, Tuple
from backend.calibration.transformations import rodrigues_to_rotation_matrix, create_homogeneous_matrix


class ChArUcoDetector:
    """
    Detector for ChArUco calibration boards.
    
    ChArUco boards combine chessboard and ArUco markers, providing:
    - Robust detection (ArUco markers)
    - Sub-pixel accuracy (chessboard corners)
    - Partial occlusion handling
    """
    
    def __init__(
        self,
        squares_x: int,
        squares_y: int,
        square_length: float,
        marker_length: float,
        dictionary_name: str = "DICT_4X4_50"
    ):
        """
        Initialize ChArUco detector.
        
        Args:
            squares_x: Number of squares in X direction
            squares_y: Number of squares in Y direction
            square_length: Length of each square (in mm)
            marker_length: Length of ArUco markers (in mm)
            dictionary_name: ArUco dictionary name (e.g., 'DICT_4X4_50')
        """
        self.squares_x = squares_x
        self.squares_y = squares_y
        self.square_length = square_length
        self.marker_length = marker_length
        self.dictionary_name = dictionary_name
        
        # Get ArUco dictionary
        dict_id = getattr(cv2.aruco, dictionary_name)
        self.aruco_dict = cv2.aruco.getPredefinedDictionary(dict_id)
        
        # Create ChArUco board
        self.board = cv2.aruco.CharucoBoard(
            (squares_x, squares_y),
            square_length,
            marker_length,
            self.aruco_dict
        )
        
        # Detector parameters
        self.detector_params = cv2.aruco.DetectorParameters()
        
        # Refine strategy for better detection
        self.refine_params = cv2.aruco.RefineParameters()
    
    def detect_charuco(self, image: np.ndarray) -> Dict:
        """
        Detect ChArUco board in an image.
        
        Args:
            image: Input image (grayscale or BGR)
            
        Returns:
            Dictionary containing:
            - detected: bool (whether board was detected)
            - corners: CharUco corners (Nx1x2 array)
            - ids: Corner IDs (Nx1 array)
            - num_corners: Number of corners detected
            - num_ids: Number of IDs detected
            - marker_corners: Detected ArUco marker corners
            - marker_ids: Detected ArUco marker IDs
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Detect ArUco markers
        marker_corners, marker_ids, rejected = cv2.aruco.detectMarkers(
            gray, 
            self.aruco_dict,
            parameters=self.detector_params
        )
        
        # Initialize result
        result = {
            'detected': False,
            'corners': None,
            'ids': None,
            'num_corners': 0,
            'num_ids': 0,
            'marker_corners': marker_corners,
            'marker_ids': marker_ids
        }
        
        # If at least one marker detected, interpolate ChArUco corners
        if marker_ids is not None and len(marker_ids) > 0:
            # Interpolate CharUco corners
            num_corners, charuco_corners, charuco_ids = cv2.aruco.interpolateCornersCharuco(
                marker_corners,
                marker_ids,
                gray,
                self.board
            )
            
            if charuco_corners is not None and charuco_ids is not None:
                result['detected'] = True
                result['corners'] = charuco_corners
                result['ids'] = charuco_ids
                result['num_corners'] = len(charuco_corners)
                result['num_ids'] = len(charuco_ids)
        
        return result
    
    def estimate_pose(
        self,
        image: np.ndarray,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray
    ) -> Dict:
        """
        Estimate camera pose from ChArUco board in image.
        
        Args:
            image: Input image
            camera_matrix: Camera intrinsic matrix (3x3)
            dist_coeffs: Distortion coefficients (5,)
            
        Returns:
            Dictionary containing:
            - success: bool (whether pose estimation succeeded)
            - rvec: Rotation vector (Rodrigues, 3x1) [if successful]
            - tvec: Translation vector (3x1) [if successful]
            - rotation_matrix: Rotation matrix (3x3) [if successful]
            - transformation_matrix: Homogeneous matrix (4x4) [if successful]
            - corners_detected: Number of corners used
            - reprojection_error: RMS reprojection error [if successful]
        """
        # Detect ChArUco board
        detection = self.detect_charuco(image)
        
        result = {
            'success': False,
            'corners_detected': detection['num_corners']
        }
        
        if not detection['detected']:
            return result
        
        # Need at least 4 corners for pose estimation
        if detection['num_corners'] < 4:
            return result
        
        # Estimate pose using ChArUco corners
        success, rvec, tvec = cv2.aruco.estimatePoseCharucoBoard(
            detection['corners'],
            detection['ids'],
            self.board,
            camera_matrix,
            dist_coeffs,
            None,
            None
        )
        
        if success:
            # Convert rvec to rotation matrix
            rotation_matrix = rodrigues_to_rotation_matrix(rvec)
            
            # Create homogeneous transformation matrix
            transformation_matrix = create_homogeneous_matrix(rotation_matrix, tvec.ravel())
            
            # Calculate reprojection error
            reprojection_error = self._calculate_reprojection_error(
                detection['corners'],
                detection['ids'],
                rvec,
                tvec,
                camera_matrix,
                dist_coeffs
            )
            
            result.update({
                'success': True,
                'rvec': rvec,
                'tvec': tvec,
                'rotation_matrix': rotation_matrix,
                'transformation_matrix': transformation_matrix,
                'reprojection_error': reprojection_error
            })
        
        return result
    
    def _calculate_reprojection_error(
        self,
        corners: np.ndarray,
        ids: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray
    ) -> float:
        """
        Calculate RMS reprojection error for detected corners.
        
        Args:
            corners: Detected ChArUco corners
            ids: Corner IDs
            rvec, tvec: Estimated pose
            camera_matrix, dist_coeffs: Camera parameters
            
        Returns:
            RMS reprojection error in pixels
        """
        # Get 3D object points for detected corners
        obj_points = self.board.getChessboardCorners()[ids.ravel()]
        
        # Project 3D points to image
        projected_points, _ = cv2.projectPoints(
            obj_points,
            rvec,
            tvec,
            camera_matrix,
            dist_coeffs
        )
        
        # Calculate euclidean distance between detected and projected
        errors = np.linalg.norm(corners - projected_points, axis=2)
        
        # Return RMS error
        return np.sqrt(np.mean(errors ** 2))
    
    def draw_detected_board(
        self,
        image: np.ndarray,
        corners: np.ndarray,
        ids: np.ndarray
    ) -> np.ndarray:
        """
        Draw detected ChArUco corners on image for visualization.
        
        Args:
            image: Input image
            corners: Detected corners
            ids: Corner IDs
            
        Returns:
            Image with drawn corners
        """
        output = image.copy()
        if corners is not None and ids is not None:
            cv2.aruco.drawDetectedCornersCharuco(output, corners, ids)
        return output
    
    def draw_axis(
        self,
        image: np.ndarray,
        rvec: np.ndarray,
        tvec: np.ndarray,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        length: float = None
    ) -> np.ndarray:
        """
        Draw coordinate system axis on image.
        
        Args:
            image: Input image
            rvec, tvec: Camera pose
            camera_matrix, dist_coeffs: Camera parameters
            length: Axis length (default: square_length)
            
        Returns:
            Image with drawn axis
        """
        if length is None:
            length = self.square_length
        
        output = image.copy()
        cv2.drawFrameAxes(output, camera_matrix, dist_coeffs, rvec, tvec, length)
        return output
