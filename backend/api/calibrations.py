"""
FastAPI router for calibration endpoints.
Handles CRUD operations, image uploads, robot poses, and calibration execution.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pathlib import Path
from datetime import datetime

from backend.database import get_db
from backend.models import User, CalibrationRun, RobotPose, CalibrationImage, CameraPose
from backend.models.calibration import CalibrationStatus, RobotPoseInputMethod
from backend.schemas.calibration import (
    CalibrationRunCreate,
    CalibrationRunResponse,
    RobotPoseCreate,
    RobotPoseResponse,
    CalibrationImageResponse,
    CameraPoseResponse,
    CalibrationExecuteResponse,
    CSVImportResponse,
    ImageUploadResponse
)
from backend.auth.dependencies import get_current_active_user, require_engineer
from backend.utils.file_utils import (
    validate_image_file,
    save_uploaded_image,
    parse_robot_poses_csv,
    get_image_dimensions
)
from backend.calibration import CalibrationService
from backend.calibration.transformations import euler_to_rotation_matrix

router = APIRouter()


# ============================================================================
# CRUD Operations for Calibrations
# ============================================================================

@router.post("/calibrations", response_model=CalibrationRunResponse, status_code=status.HTTP_201_CREATED)
def create_calibration(
    calibration: CalibrationRunCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new calibration run.
    
    Requiere autenticación. Cualquier usuario puede crear calibraciones.
    """
    # Get default algorithm parameters (assume ID=1 from init_db.py)
    new_calibration = CalibrationRun(
        name=calibration.name,
        description=calibration.description,
        status=CalibrationStatus.PENDING,
        charuco_squares_x=calibration.charuco_squares_x,
        charuco_squares_y=calibration.charuco_squares_y,
        charuco_square_length=calibration.charuco_square_length,
        charuco_marker_length=calibration.charuco_marker_length,
        charuco_dictionary=calibration.charuco_dictionary,
        user_id=current_user.id,
        algorithm_params_id=1  # Default algorithm params
    )
    
    db.add(new_calibration)
    db.commit()
    db.refresh(new_calibration)
    
    return new_calibration


@router.get("/calibrations", response_model=List[CalibrationRunResponse])
def list_calibrations(
    skip: int = 0,
    limit: int = 100,
    status: Optional[CalibrationStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List calibration runs with optional status filter.
    
    Users can only see their own calibrations unless they are engineers.
    """
    query = db.query(CalibrationRun)
    
    # Filter by status if provided
    if status:
        query = query.filter(CalibrationRun.status == status)
    
    # Non-engineers can only see their own calibrations
    if current_user.role.value != "engineer" and current_user.role.value != "supervisor":
        query = query.filter(CalibrationRun.user_id == current_user.id)
    
    calibrations = query.offset(skip).limit(limit).all()
    return calibrations


@router.get("/calibrations/{calibration_id}", response_model=CalibrationRunResponse)
def get_calibration(
    calibration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed information about a specific calibration run."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    # Check permissions (only creator or engineers can view)
    if calibration.user_id != current_user.id and current_user.role.value not in ["engineer", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized to view this calibration")
    
    return calibration


@router.delete("/calibrations/{calibration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calibration(
    calibration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_engineer)
):
    """Delete a calibration run. Only engineers can delete."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    # Delete associated images from disk
    images = db.query(CalibrationImage).filter(CalibrationImage.calibration_run_id == calibration_id).all()
    for img in images:
        try:
            Path(img.image_path).unlink(missing_ok=True)
        except:
            pass  # Continue even if file deletion fails
    
    db.delete(calibration)
    db.commit()


# ============================================================================
# Image Upload
# ============================================================================

@router.post("/calibrations/{calibration_id}/upload-images", response_model=ImageUploadResponse)
async def upload_images(
    calibration_id: int,
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload ChArUco images for a calibration.
    
    - Maximum 20 images
    - Allowed formats: PNG, JPG, JPEG
    - Images are saved with structured filenames
    """
    # Verify calibration exists and user has permission
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    if calibration.user_id != current_user.id and current_user.role.value not in ["engineer", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if calibration.status != CalibrationStatus.PENDING:
        raise HTTPException(status_code=400, detail="Cannot upload images to non-pending calibration")
    
    # Validate number of files
    if len(files) > 20:
        raise HTTPException(status_code=400, detail="Maximum 20 images allowed")
    
    uploaded_filenames = []
    errors = []
    
    # Get next pose_index
    existing_count = db.query(CalibrationImage).filter(
        CalibrationImage.calibration_run_id == calibration_id
    ).count()
    
    for idx, file in enumerate(files, start=existing_count + 1):
        try:
            # Validate file
            validate_image_file(file)
            
            # Save file
            saved_path = await save_uploaded_image(file, calibration_id, idx)
            
            # Get image dimensions
            width, height = get_image_dimensions(saved_path)
            
            # Create database record
            calib_image = CalibrationImage(
                calibration_run_id=calibration_id,
                pose_index=idx,
                image_path=str(saved_path),
                original_filename=file.filename,
                file_size_bytes=saved_path.stat().st_size if saved_path.exists() else 0,
                image_width=width,
                image_height=height
            )
            
            db.add(calib_image)
            uploaded_filenames.append(file.filename)
            
        except HTTPException as e:
            errors.append(f"{file.filename}: {e.detail}")
        except Exception as e:
            errors.append(f"{file.filename}: {str(e)}")
    
    db.commit()
    
    return ImageUploadResponse(
        success=len(uploaded_filenames) > 0,
        images_uploaded=len(uploaded_filenames),
        filenames=uploaded_filenames,
        errors=errors
    )


# ============================================================================
# Robot Poses
# ============================================================================

@router.post("/calibrations/{calibration_id}/robot-poses", response_model=RobotPoseResponse)
def add_robot_pose(
    calibration_id: int,
    pose: RobotPoseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Add a single robot pose manually."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    if calibration.user_id != current_user.id and current_user.role.value not in ["engineer", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Check if pose_index already exists
    existing = db.query(RobotPose).filter(
        RobotPose.calibration_run_id == calibration_id,
        RobotPose.pose_index == pose.pose_index
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail=f"Pose with index {pose.pose_index} already exists")
    
    robot_pose = RobotPose(
        calibration_run_id=calibration_id,
        pose_index=pose.pose_index,
        x=pose.x,
        y=pose.y,
        z=pose.z,
        rx=pose.rx,
        ry=pose.ry,
        rz=pose.rz,
        input_method=RobotPoseInputMethod.MANUAL_ENTRY,
        rotation_matrix=euler_to_rotation_matrix(pose.rx, pose.ry, pose.rz, degrees=True).tolist(),
        translation_vector=[pose.x, pose.y, pose.z]
    )
    
    db.add(robot_pose)
    
    # Update calibration's input method
    if calibration.robot_poses_input_method is None:
        calibration.robot_poses_input_method = RobotPoseInputMethod.MANUAL_ENTRY
    elif calibration.robot_poses_input_method == RobotPoseInputMethod.CSV_IMPORT:
        calibration.robot_poses_input_method = RobotPoseInputMethod.MIXED
    
    db.commit()
    db.refresh(robot_pose)
    
    return robot_pose


@router.post("/calibrations/{calibration_id}/import-robot-poses-csv", response_model=CSVImportResponse)
async def import_robot_poses_csv(
    calibration_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Import robot poses from CSV file."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    if calibration.user_id != current_user.id and current_user.role.value not in ["engineer", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Read and parse CSV
    try:
        content = await file.read()
        poses = parse_robot_poses_csv(content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing CSV: {str(e)}")
    
    errors = []
    imported_count = 0
    
    for pose_data in poses:
        try:
            # Check if pose_index already exists
            existing = db.query(RobotPose).filter(
                RobotPose.calibration_run_id == calibration_id,
                RobotPose.pose_index == pose_data['pose_index']
            ).first()
            
            if existing:
                errors.append(f"Pose {pose_data['pose_index']} already exists, skipping")
                continue
            
            # Calculate matrices
            try:
                rot_mat = euler_to_rotation_matrix(pose_data['rx'], pose_data['ry'], pose_data['rz'], degrees=True).tolist()
                trans_vec = [pose_data['x'], pose_data['y'], pose_data['z']]
            except Exception as e:
                errors.append(f"Error calculating matrices for pose {pose_data['pose_index']}: {str(e)}")
                continue

            robot_pose = RobotPose(
                calibration_run_id=calibration_id,
                pose_index=pose_data['pose_index'],
                x=pose_data['x'],
                y=pose_data['y'],
                z=pose_data['z'],
                rx=pose_data['rx'],
                ry=pose_data['ry'],
                rz=pose_data['rz'],
                input_method=RobotPoseInputMethod.CSV_IMPORT,
                rotation_matrix=rot_mat,
                translation_vector=trans_vec
            )
            db.add(robot_pose)
            imported_count += 1
            
        except Exception as e:
            errors.append(f"Pose {pose_data.get('pose_index')}: {str(e)}")
    
    # Update calibration metadata
    try:
        calibration.robot_poses_input_method = RobotPoseInputMethod.CSV_IMPORT
        calibration.csv_filename = file.filename
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return CSVImportResponse(
        success=imported_count > 0,
        poses_imported=imported_count,
        filename=file.filename,
        errors=errors
    )


@router.get("/calibrations/{calibration_id}/robot-poses", response_model=List[RobotPoseResponse])
def list_robot_poses(
    calibration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all robot poses for a calibration."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    poses = db.query(RobotPose).filter(
        RobotPose.calibration_run_id == calibration_id
    ).order_by(RobotPose.pose_index).all()
    
    return poses


# ============================================================================
# Execute Calibration
# ============================================================================

@router.post("/calibrations/{calibration_id}/execute", response_model=CalibrationExecuteResponse)
def execute_calibration(
    calibration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Execute hand-eye calibration.
    
    Processes images, detects ChArUco boards, calculates camera poses,
    and runs Tsai-Lenz algorithm.
    """
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    if calibration.user_id != current_user.id and current_user.role.value not in ["engineer", "supervisor"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if calibration.status != CalibrationStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute calibration with status {calibration.status.value}"
        )
    
    # Update status to processing
    calibration.status = CalibrationStatus.PROCESSING
    db.commit()
    
    # Execute calibration using service
    try:
        service = CalibrationService(db)
        result = service.process_calibration_run(calibration_id)
        
        if result['success']:
            return CalibrationExecuteResponse(
                success=True,
                calibration_id=calibration_id,
                transformation_matrix=result['transformation_matrix'],
                reprojection_error=result.get('reprojection_error'),
                rotation_error_deg=result.get('rotation_error_deg'),
                translation_error_mm=result.get('translation_error_mm'),
                poses_processed=result['poses_processed'],
                poses_valid=result['poses_valid'],
                method=result.get('method')
            )
        else:
            # Rollback status to pending on failure
            calibration.status = CalibrationStatus.FAILED
            db.commit()
            
            return CalibrationExecuteResponse(
                success=False,
                calibration_id=calibration_id,
                transformation_matrix=None,
                poses_processed=0,
                poses_valid=0,
                error_message=result.get('error_message', 'Calibration failed')
            )
            
    except Exception as e:
        # Mark as failed
        calibration.status = CalibrationStatus.FAILED
        db.commit()
        
        return CalibrationExecuteResponse(
            success=False,
            calibration_id=calibration_id,
            transformation_matrix=None,
            poses_processed=0,
            poses_valid=0,
            error_message=str(e)
        )


# ============================================================================
# Query Results
# ============================================================================

@router.get("/calibrations/{calibration_id}/images", response_model=List[CalibrationImageResponse])
def list_images(
    calibration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all images for a calibration with detection status."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    images = db.query(CalibrationImage).filter(
        CalibrationImage.calibration_run_id == calibration_id
    ).order_by(CalibrationImage.pose_index).all()
    
    return images


@router.get("/calibrations/{calibration_id}/camera-poses", response_model=List[CameraPoseResponse])
def list_camera_poses(
    calibration_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """List all computed camera poses for a calibration."""
    calibration = db.query(CalibrationRun).filter(CalibrationRun.id == calibration_id).first()
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    camera_poses = db.query(CameraPose).filter(
        CameraPose.calibration_run_id == calibration_id
    ).order_by(CameraPose.pose_index).all()
    
    return camera_poses
