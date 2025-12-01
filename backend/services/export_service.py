"""
Export service for calibration results.
Provides functionality to export calibration data in multiple formats (JSON, CSV, TXT).
"""
import json
from typing import Dict, Any
from backend.models.calibration import CalibrationRun


class ExportService:
    """Service for exporting calibration results in different formats."""
    
    @staticmethod
    def export_to_json(calibration: CalibrationRun) -> str:
        """
        Export complete calibration data as JSON.
        
        Args:
            calibration: CalibrationRun instance
            
        Returns:
            JSON string with complete calibration data
        """
        data = {
            "calibration_id": calibration.id,
            "name": calibration.name,
            "description": calibration.description,
            "status": calibration.status,
            "created_at": calibration.created_at.isoformat() if calibration.created_at else None,
            "transformation_matrix": calibration.transformation_matrix,
            "metrics": {
                "reprojection_error": calibration.reprojection_error,
                "rotation_error_deg": calibration.rotation_error_deg,
                "translation_error_mm": calibration.translation_error_mm,
                "poses_valid": calibration.poses_valid,
                "poses_processed": calibration.poses_processed
            },
            "parameters": {
                "charuco_squares_x": calibration.charuco_squares_x,
                "charuco_squares_y": calibration.charuco_squares_y,
                "charuco_square_length": calibration.charuco_square_length,
                "charuco_marker_length": calibration.charuco_marker_length,
                "charuco_dictionary": calibration.charuco_dictionary
            },
            "method": calibration.method
        }
        
        return json.dumps(data, indent=2)
    
    @staticmethod
    def export_to_csv(calibration: CalibrationRun) -> str:
        """
        Export transformation matrix as CSV.
        
        Args:
            calibration: CalibrationRun instance
            
        Returns:
            CSV string with transformation matrix
        """
        matrix = calibration.transformation_matrix
        
        # Handle case where matrix might be a JSON string
        if isinstance(matrix, str):
            matrix = json.loads(matrix)
        
        # Create CSV header
        csv_lines = [
            "# Hand-Eye Calibration Transformation Matrix",
            f"# Calibration: {calibration.name}",
            f"# ID: {calibration.id}",
            f"# Status: {calibration.status}",
            "#",
            "# Transformation Matrix (4x4):"
        ]
        
        # Add matrix rows
        for row in matrix:
            csv_lines.append(",".join(str(val) for val in row))
        
        # Add metrics as comments
        csv_lines.extend([
            "#",
            "# Metrics:",
            f"# Reprojection Error: {calibration.reprojection_error}",
            f"# Rotation Error (deg): {calibration.rotation_error_deg}",
            f"# Translation Error (mm): {calibration.translation_error_mm}",
            f"# Poses Valid/Processed: {calibration.poses_valid}/{calibration.poses_processed}"
        ])
        
        return "\n".join(csv_lines)
    
    @staticmethod
    def export_to_txt(calibration: CalibrationRun) -> str:
        """
        Export human-readable summary as TXT.
        
        Args:
            calibration: CalibrationRun instance
            
        Returns:
            TXT string with human-readable summary
        """
        matrix = calibration.transformation_matrix
        
        # Handle case where matrix might be a JSON string
        if isinstance(matrix, str):
            matrix = json.loads(matrix)
        
        lines = [
            "=" * 70,
            "HAND-EYE CALIBRATION RESULTS",
            "=" * 70,
            "",
            f"Calibration Name: {calibration.name}",
            f"ID: {calibration.id}",
            f"Status: {calibration.status}",
            f"Date: {calibration.created_at.strftime('%Y-%m-%d %H:%M:%S') if calibration.created_at else 'N/A'}",
            f"Method: {calibration.method or 'Tsai-Lenz'}",
            "",
            "-" * 70,
            "TRANSFORMATION MATRIX (Camera to End-Effector)",
            "-" * 70,
            ""
        ]
        
        # Format matrix
        for row in matrix:
            formatted_row = "  ".join(f"{val:12.6f}" for val in row)
            lines.append(f"  [ {formatted_row} ]")
        
        lines.extend([
            "",
            "-" * 70,
            "CALIBRATION METRICS",
            "-" * 70,
            f"  Reprojection Error:    {calibration.reprojection_error:.4f}",
            f"  Rotation Error:        {calibration.rotation_error_deg:.4f} degrees",
            f"  Translation Error:     {calibration.translation_error_mm:.4f} mm",
            f"  Valid Poses:           {calibration.poses_valid}/{calibration.poses_processed}",
            "",
            "-" * 70,
            "CHARUCO BOARD PARAMETERS",
            "-" * 70,
            f"  Squares (X x Y):       {calibration.charuco_squares_x} x {calibration.charuco_squares_y}",
            f"  Square Length:         {calibration.charuco_square_length} mm",
            f"  Marker Length:         {calibration.charuco_marker_length} mm",
            f"  Dictionary:            {calibration.charuco_dictionary}",
            "",
            "=" * 70,
            ""
        ])
        
        return "\n".join(lines)
