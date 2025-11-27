"""
ChArUco detection and visualization utilities.
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def detect_and_annotate_charuco(
    image_path: Path,
    output_path: Path,
    squares_x: int,
    squares_y: int,
    square_length: float,
    marker_length: float,
    dictionary_name: str = "DICT_5X5_100"
) -> Tuple[bool, int, int]:
    """
    Detect ChArUco board in image and save annotated version.
    
    Args:
        image_path: Path to original image
        output_path: Path to save annotated image
        squares_x: Number of squares in X direction
        squares_y: Number of squares in Y direction
        square_length: Size of chessboard square (mm)
        marker_length: Size of ArUco marker (mm)
        dictionary_name: ArUco dictionary name
    
    Returns:
        Tuple of (detected: bool, corners_count: int, ids_count: int, corners_data: list, ids_data: list)
    """
    try:
        # Load image
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"❌ Failed to load image: {image_path}")
            logger.error(f"Failed to load image: {image_path}")
            return False, 0, 0, None, None
        
        print(f"🔍 Processing image: {image_path}")
        print(f"📐 Board config: {squares_x}x{squares_y} squares, square={square_length}mm, marker={marker_length}mm, dict={dictionary_name}")
        print(f"✅ Expected corners: {(squares_x-1) * (squares_y-1)}")
        
        # Get ArUco dictionary
        aruco_dict = cv2.aruco.getPredefinedDictionary(
            getattr(cv2.aruco, dictionary_name)
        )
        
        # Create ChArUco board
        board = cv2.aruco.CharucoBoard(
            (squares_x, squares_y),
            square_length,
            marker_length,
            aruco_dict
        )
        
        print(f"🎯 Board created: {board.getChessboardSize()}")
        
        # Detect markers and ChArUco corners using modern API
        detector_params = cv2.aruco.DetectorParameters()
        aruco_detector = cv2.aruco.ArucoDetector(aruco_dict, detector_params)
        corners, ids, rejected = aruco_detector.detectMarkers(image)
        
        # Create annotated image
        annotated = image.copy()
        detected = False
        corners_count = 0
        ids_count = 0
        
        if ids is not None and len(ids) > 0:
            # Draw detected markers
            cv2.aruco.drawDetectedMarkers(annotated, corners, ids)
            
            print(f"📍 Detected {len(ids)} ArUco markers")
            
            # Use CharucoDetector for modern OpenCV (4.7+)
            try:
                charuco_detector = cv2.aruco.CharucoDetector(board)
                charuco_corners, charuco_ids, marker_corners, marker_ids = charuco_detector.detectBoard(image)
                
                if charuco_corners is not None and len(charuco_corners) > 0:
                    detected = True
                    corners_count = len(charuco_corners)
                    ids_count = len(charuco_ids) if charuco_ids is not None else 0
                    
                    print(f"✅ FINAL: detected={detected}, corners_count={corners_count}, ids_count={ids_count}")
                    
                    # Convert numpy arrays to Python lists for JSON serialization
                    corners_data = charuco_corners.reshape(-1, 2).tolist() if charuco_corners is not None else None
                    ids_data = charuco_ids.flatten().tolist() if charuco_ids is not None else None
                    
                    # Draw ChArUco corners
                    cv2.aruco.drawDetectedCornersCharuco(annotated, charuco_corners, charuco_ids)
                    
                    # Add detection info text
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text = f"ChArUco Detected: {corners_count} corners"
                    cv2.putText(annotated, text, (10, 30), font, 1, (0, 255, 0), 2)
                else:
                    # Markers detected but no ChArUco
                    text = "ArUco markers found, ChArUco interpolation failed"
                    cv2.putText(annotated, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            except Exception as e:
                print(f"⚠️  CharucoDetector failed: {e}, corners will not be detected")
                text = f"Error: {str(e)[:50]}"
                cv2.putText(annotated, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # No markers detected
            text = "No ChArUco pattern detected"
            cv2.putText(annotated, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        # Save annotated image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), annotated)
        
        logger.info(f"ChArUco detection: detected={detected}, corners={corners_count}, ids={ids_count}")
        return detected, corners_count, ids_count, corners_data, ids_data
        
    except Exception as e:
        logger.error(f"Error in ChArUco detection: {e}")
        return False, 0, 0, None, None
