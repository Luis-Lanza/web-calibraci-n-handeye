"""
Calibration service that orchestrates the complete hand-eye calibration process.
Processes images, detects ChArUco boards, estimates poses, and runs calibration algorithm.
"""
import cv2
import numpy as np
from pathlib import Path
from sqlalchemy.orm import Session
from typing import Dict, List, Optional
from datetime import datetime

from backend.models import CalibrationRun, CalibrationImage, RobotPose, CameraPose
from backend.models.calibration import CalibrationStatus
from backend.calibration.charuco_detector import ChArUcoDetector
from backend.calibration.camera_params import get_default_camera_matrix, get_default_distortion_coeffs
from backend.calibration.transformations import pose_euler_to_matrix
from backend.calibration.tsai_lenz import solve_hand_eye_tsai_lenz, validate_pose_pairs
from backend.calibration.error_metrics import calculate_reprojection_error, calculate_pose_diversity


class CalibrationService:
    """
    Service for processing hand-eye calibrations.
    
    Workflow:
    1. Load calibration run from database
    2. Load and process images (detect ChArUco)
    3. Estimate camera poses from detected boards
    4. Load robot poses and convert to matrices
    5. Run Tsai-Lenz algorithm
    6. Calculate errors
    7. Save results to database
    """
    
    def __init__(self, db: Session):
        """
        Initialize calibration service.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def process_calibration_run(self, calibration_run_id: int) -> Dict:
        """
        Process a complete calibration run.
        
        Args:
            calibration_run_id: ID of the CalibrationRun to process
            
        Returns:
            Dictionary with:
            - success: bool
            - transformation_matrix: 4x4 matrix (as list) if successful  
            - reprojection_error: float if successful
            - poses_processed: int
            - poses_valid: int
            - error_message: str if failed
        """
        try:
            # Load calibration run
            calib_run = self.db.query(CalibrationRun).filter(
                CalibrationRun.id == calibration_run_id
            ).first()
            
            if not calib_run:
                return {
                    'success': False,
                    'error_message': f'Calibration run {calibration_run_id} not found'
                }
            
            # Initialize ChArUco detector
            detector = ChArUcoDetector(
                squares_x=calib_run.charuco_squares_x,
                squares_y=calib_run.charuco_squares_y,
                square_length=calib_run.charuco_square_length,
                marker_length=calib_run.charuco_marker_length,
                dictionary_name=calib_run.charuco_dictionary
            )
            
            # Get camera parameters (using defaults for now)
            camera_matrix = get_default_camera_matrix()
            dist_coeffs = get_default_distortion_coeffs()
            
            # Process images and estimate camera poses
            camera_poses_result = self._process_images_and_estimate_poses(
                calib_run,
                detector,
                camera_matrix,
                dist_coeffs
            )
            
            if not camera_poses_result['success']:
                return camera_poses_result
            
            # Load robot poses and convert to matrices
            robot_poses_matrices = self._load_robot_poses_as_matrices(calib_run)
            
            if len(robot_poses_matrices) == 0:
                return {
                    'success': False,
                    'error_message': 'No robot poses found'
                }
            
            # Get camera pose matrices (only successful detections)
            camera_poses_matrices = camera_poses_result['camera_poses']
            
            # Validate poses
            validation = validate_pose_pairs(robot_poses_matrices, camera_poses_matrices)
            
            if not validation['valid']:
                return {
                    'success': False,
                    'error_message': f"Pose validation failed: {'; '.join(validation['errors'])}"
                }
            
            # Run calibration algorithm
            calib_result = solve_hand_eye_tsai_lenz(robot_poses_matrices, camera_poses_matrices)
            
            # Calculate errors
            error_metrics = calculate_reprojection_error(
                calib_result['X'],
                robot_poses_matrices,
                camera_poses_matrices
            )
            
            # Calculate pose diversity (for informational purposes)
            robot_diversity = calculate_pose_diversity(robot_poses_matrices)
            
            # Save results to database
            self._save_results(calib_run, calib_result, error_metrics)
            
            return {
                'success': True,
                'transformation_matrix': calib_result['X'].tolist(),
                'reprojection_error': error_metrics['mean_error'],
                'rotation_error_deg': error_metrics['mean_rotation_error_deg'],
                'translation_error_mm': error_metrics['mean_translation_error_mm'],
                'poses_processed': len(robot_poses_matrices),
                'poses_valid': len(camera_poses_matrices),
                'method': calib_result['method_name'],
                'robot_pose_diversity': robot_diversity
            }
            
        except Exception as e:
            # Mark calibration as failed
            calib_run = self.db.query(CalibrationRun).filter(
                CalibrationRun.id == calibration_run_id
            ).first()
            
            if calib_run:
                calib_run.status = CalibrationStatus.FAILED
                self.db.commit()
            
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def _process_images_and_estimate_poses(
        self,
        calib_run: CalibrationRun,
        detector: ChArUcoDetector,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray
    ) -> Dict:
        """Process all images and estimate camera poses."""
        
        # Load images from database
        images = self.db.query(CalibrationImage).filter(
            CalibrationImage.calibration_run_id == calib_run.id
        ).order_by(CalibrationImage.pose_index).all()
        
        if len(images) == 0:
            return {
                'success': False,
                'error_message': 'No images found for calibration'
            }
        
        camera_poses = []
        successful_count = 0
        
        for calib_image in images:
            # Read image from disk
            image_path = Path(calib_image.image_path)
            
            if not image_path.exists():
                print(f"Warning: Image not found: {image_path}")
                continue
            
            image = cv2.imread(str(image_path))
            
            if image is None:
                print(f"Warning: Could not read image: {image_path}")
                continue
            
            # Estimate pose
            pose_result = detector.estimate_pose(image, camera_matrix, dist_coeffs)
            
            # Update CalibrationImage with detection results
            calib_image.charuco_detected = pose_result['success']
            calib_image.corners_detected = pose_result['corners_detected']
            
            if pose_result['success']:
                # Create CameraPose in database
                camera_pose = CameraPose(
                    calibration_run_id=calib_run.id,
                    pose_index=calib_image.pose_index,
                    rotation_matrix=pose_result['rotation_matrix'].tolist(),
                    translation_vector=pose_result['tvec'].ravel().tolist(),
                    computed_automatically=True,
                    reprojection_error_individual=pose_result['reprojection_error'],
                    computed_at=datetime.utcnow()
                )
                
                self.db.add(camera_pose)
                self.db.flush()  # Get the ID
                
                # Link image to camera pose
                calib_image.camera_pose_id = camera_pose.id
                
                # Add to result list
                camera_poses.append(pose_result['transformation_matrix'])
                successful_count += 1
        
        self.db.commit()
        
        if successful_count == 0:
            return {
                'success': False,
                'error_message': 'No ChArUco boards detected in any image'
            }
        
        if successful_count < 3:
            return {
                'success': False,
                'error_message': f'Only {successful_count} boards detected, need at least 3'
            }
        
        return {
            'success': True,
            'camera_poses': camera_poses,
            'detected_count': successful_count,
            'total_count': len(images)
        }
    
    def _load_robot_poses_as_matrices(self, calib_run: CalibrationRun) -> List[np.ndarray]:
        """Load robot poses from database and convert to 4x4 matrices."""
        
        robot_poses = self.db.query(RobotPose).filter(
            RobotPose.calibration_run_id == calib_run.id
        ).order_by(RobotPose.pose_index).all()
        
        matrices = []
        
        for robot_pose in robot_poses:
            # Convert from X,Y,Z,Rx,Ry,Rz to 4x4 matrix
            T = pose_euler_to_matrix(
                robot_pose.x,
                robot_pose.y,
                robot_pose.z,
                robot_pose.rx,
                robot_pose.ry,
                robot_pose.rz,
                degrees=True  # Assuming degrees in database
            )
            
            matrices.append(T)
        
        return matrices
    
    def _save_results(
        self,
        calib_run: CalibrationRun,
        calib_result: Dict,
        error_metrics: Dict
    ) -> None:
        """Save calibration results to database."""
        
        # Update calibration run with results
        calib_run.transformation_matrix = calib_result['X'].tolist()
        calib_run.reprojection_error = error_metrics['mean_error']
        calib_run.status = CalibrationStatus.COMPLETED
        
        self.db.commit()
