"""
File handling utilities for calibration images and CSV files.
"""
import os
import csv
import io
from pathlib import Path
from typing import List, Dict
from fastapi import UploadFile, HTTPException
from backend.config import settings


def validate_image_file(file: UploadFile) -> bool:
    """
    Validate that uploaded file is a valid image.
    
    Args:
        file: Uploaded file
        
    Returns:
        True if valid
        
    Raises:
        HTTPException: If file is invalid
    """
    # Check extension
    ext = Path(file.filename).suffix.lower()
    if ext not in settings.ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file extension {ext}. Allowed: {settings.ALLOWED_IMAGE_EXTENSIONS}"
        )
    
    # Check file size (if we can get it)
    if hasattr(file, 'size') and file.size:
        max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        if file.size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.MAX_IMAGE_SIZE_MB} MB"
            )
    
    return True


async def save_uploaded_image(
    file: UploadFile,
    calibration_id: int,
    pose_index: int,
    upload_dir: Path = None
) -> Path:
    """
    Save uploaded image to disk with structured filename and directory.
    
    Args:
        file: Uploaded file
        calibration_id: ID of calibration run
        pose_index: Index of pose (for filename)
        upload_dir: Base upload directory (default: from settings)
        
    Returns:
        Relative path to saved file
    """
    if upload_dir is None:
        upload_dir = Path(settings.UPLOAD_DIR)
    
    # Create calibration-specific subdirectory
    calib_dir = upload_dir / f"calibration_{calibration_id}"
    calib_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename
    ext = Path(file.filename).suffix.lower()
    filename = f"img_{pose_index:02d}{ext}"
    filepath = calib_dir / filename
    
    # Save file
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)
    
    # Return relative path (relative to project root)
    return filepath


def parse_robot_poses_csv(file_content: bytes) -> List[Dict]:
    """
    Parse CSV file containing robot poses.
    
    Supports headers:
    - X,Y,Z,A,B,C (uppercase)
    - x,y,z,rx,ry,rz (lowercase)
    
    Args:
        file_content: CSV file content as bytes
        
    Returns:
        List of pose dictionaries with keys: pose_index, x, y, z, rx, ry, rz
        
    Raises:
        HTTPException: If CSV is invalid
    """
    # Decode content
    try:
        content_str = file_content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    
    # Parse CSV
    reader = csv.DictReader(io.StringIO(content_str))
    
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty")
    
    # Map headers (support both X,Y,Z,A,B,C and x,y,z,rx,ry,rz)
    header_mappings = {
        'X': 'x', 'Y': 'y', 'Z': 'z',
        'A': 'rx', 'B': 'ry', 'C': 'rz',
        'x': 'x', 'y': 'y', 'z': 'z',
        'rx': 'rx', 'ry': 'ry', 'rz': 'rz'
    }
    
    # Check required headers
    has_position = any(h in reader.fieldnames for h in ['X', 'x'])
    has_rotation = any(h in reader.fieldnames for h in ['A', 'rx'])
    
    if not (has_position and has_rotation):
        raise HTTPException(
            status_code=400,
            detail="CSV must have position (X,Y,Z or x,y,z) and rotation (A,B,C or rx,ry,rz) columns"
        )
    
    poses = []
    for idx, row in enumerate(reader, start=1):
        try:
            pose = {
                'pose_index': idx,
                'x': float(row.get('X') or row.get('x')),
                'y': float(row.get('Y') or row.get('y')),
                'z': float(row.get('Z') or row.get('z')),
                'rx': float(row.get('A') or row.get('rx')),
                'ry': float(row.get('B') or row.get('ry')),
                'rz': float(row.get('C') or row.get('rz'))
            }
            poses.append(pose)
        except (ValueError, TypeError, KeyError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error parsing row {idx}: {str(e)}"
            )
    
    if len(poses) == 0:
        raise HTTPException(status_code=400, detail="CSV file contains no data rows")
    
    return poses


def get_image_dimensions(filepath: Path) -> tuple:
    """
    Get image dimensions without loading full image.
    
    Args:
        filepath: Path to image file
        
    Returns:
        Tuple of (width, height) or (None, None) if unable to determine
    """
    try:
        import cv2
        img = cv2.imread(str(filepath))
        if img is not None:
            height, width = img.shape[:2]
            return width, height
    except:
        pass
    
    return None, None
