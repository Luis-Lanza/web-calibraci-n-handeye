"""
Test script for the hand-eye calibration engine using real data.
Tests the complete calibration pipeline with example images and robot poses.
"""
import sys
from pathlib import Path
import csv
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.calibration import (
    ChArUcoDetector,
    pose_euler_to_matrix,
    solve_hand_eye_tsai_lenz,
    calculate_reprojection_error,
    calculate_pose_diversity,
    get_default_camera_matrix,
    get_default_distortion_coeffs
)
import cv2


def load_robot_poses_from_csv(csv_path: Path):
    """Load robot poses from CSV file."""
    poses = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            # Parse pose data (X, Y, Z in mm, A, B, C in degrees)
            x = float(row['X'])
            y = float(row['Y'])
            z = float(row['Z'])
            rx = float(row['A'])  # A = Rx
            ry = float(row['B'])  # B = Ry
            rz = float(row['C'])  # C = Rz
            
            # Convert to 4x4 transformation matrix
            T = pose_euler_to_matrix(x, y, z, rx, ry, rz, degrees=True)
            poses.append({
                'index': i + 1,
                'x': x, 'y': y, 'z': z,
                'rx': rx, 'ry': ry, 'rz': rz,
                'matrix': T
            })
    
    return poses


def test_charuco_detection():
    """Test ChArUco detection on example images."""
    print("="*80)
    print("TEST 1: ChArUco Detection")
    print("="*80)
    
    # Initialize detector with CORRECT parameters from user's setup
    detector = ChArUcoDetector(
        squares_x=7,              # 7 cuadros en X
        squares_y=5,              # 5 cuadros en Y
        square_length=100.0,      # 100 mm (no 40!)
        marker_length=75.0,       # 75 mm (no 30!)
        dictionary_name="DICT_5X5_100"  # DICT_5X5_100 (no DICT_4X4_50!)
    )
    
    # Use REAL camera parameters from user's calibration
    camera_matrix = np.array([
        [1106.8873,    0.0,         786.64098],
        [0.0,          1118.7950,   602.70481],
        [0.0,          0.0,         1.0]
    ], dtype=np.float32)
    
    dist_coeffs = np.array([
        0.009970987168925539,
        -0.07011415957754046,
        1.850066041151057e-05,
        -0.0010577712232235493,
        -0.004862828904276413,
        -0.00981920166785844,
        0.04003206585742406,
        -0.057584865291165986
    ], dtype=np.float32)
    
    print(f"\nChArUco Board Parameters:")
    print(f"  Size: 7x5 squares")
    print(f"  Square length: 100 mm")
    print(f"  Marker length: 75 mm")
    print(f"  Dictionary: DICT_5X5_100")
    
    print(f"\nCamera Parameters:")
    print(f"  Focal length: fx={camera_matrix[0,0]:.2f}, fy={camera_matrix[1,1]:.2f}")
    print(f"  Principal point: cx={camera_matrix[0,2]:.2f}, cy={camera_matrix[1,2]:.2f}")
    print(f"  Distortion coefficients: {len(dist_coeffs)} parameters")
    
    # Test images directory
    images_dir = Path("data/examples")
    image_files = sorted(images_dir.glob("*.png"))
    
    if not image_files:
        print("❌ No images found in data/examples/")
        return [], detector, camera_matrix, dist_coeffs
    
    print(f"\nFound {len(image_files)} images")
    
    camera_poses = []
    successful_detections = 0
    
    for img_file in image_files:
        print(f"\nProcessing: {img_file.name}")
        
        # Read image
        image = cv2.imread(str(img_file))
        
        if image is None:
            print(f"  ❌ Could not read image")
            continue
        
        # Detect ChArUco and estimate pose
        result = detector.estimate_pose(image, camera_matrix, dist_coeffs)
        
        if result['success']:
            print(f"  ✓ ChArUco detected")
            print(f"    Corners: {result['corners_detected']}")
            print(f"    Reproj error: {result['reprojection_error']:.2f} px")
            camera_poses.append(result['transformation_matrix'])
            successful_detections += 1
        else:
            print(f"  ❌ ChArUco NOT detected ({result['corners_detected']} corners)")
    
    print(f"\n{'='*80}")
    print(f"Summary: {successful_detections}/{len(image_files)} images successfully processed")
    print(f"{'='*80}")
    
    return camera_poses, detector, camera_matrix, dist_coeffs


def test_hand_eye_calibration(robot_poses_data, camera_poses):
    """Test hand-eye calibration with Tsai-Lenz."""
    print("\n" + "="*80)
    print("TEST 2: Hand-Eye Calibration (Tsai-Lenz)")
    print("="*80)
    
    if len(camera_poses) < 3:
        print(f"❌ Insufficient camera poses: need at least 3, got {len(camera_poses)}")
        return None
    
    # Get robot pose matrices (matching the successfully detected camera poses)
    robot_poses_matrices = [pose['matrix'] for pose in robot_poses_data[:len(camera_poses)]]
    
    print(f"\nUsing {len(robot_poses_matrices)} pose pairs")
    
    # Calculate pose diversity
    print("\n--- Pose Diversity ---")
    robot_diversity = calculate_pose_diversity(robot_poses_matrices)
    camera_diversity = calculate_pose_diversity(camera_poses)
    
    print(f"Robot poses:")
    print(f"  Mean rotation change: {robot_diversity['mean_rotation_change_deg']:.2f}°")
    print(f"  Mean translation change: {robot_diversity['mean_translation_change_mm']:.2f} mm")
    
    print(f"\nCamera poses:")
    print(f"  Mean rotation change: {camera_diversity['mean_rotation_change_deg']:.2f}°")
    print(f"  Mean translation change: {camera_diversity['mean_translation_change_mm']:.2f} mm")
    
    # Run calibration
    print("\n--- Running Tsai-Lenz Algorithm ---")
    calib_result = solve_hand_eye_tsai_lenz(robot_poses_matrices, camera_poses)
    
    print(f"✓ Calibration completed using {calib_result['method_name']}")
    
    # Calculate errors
    print("\n--- Calculating Errors ---")
    errors = calculate_reprojection_error(
        calib_result['X'],
        robot_poses_matrices,
        camera_poses
    )
    
    print(f"\nReprojection Error:")
    print(f"  Mean: {errors['mean_error']:.4f}")
    print(f"  Std:  {errors['std_error']:.4f}")
    print(f"  Max:  {errors['max_error']:.4f}")
    print(f"  Min:  {errors['min_error']:.4f}")
    
    print(f"\nRotation Error:")
    print(f"  Mean: {errors['mean_rotation_error_deg']:.4f}°")
    
    print(f"\nTranslation Error:")
    print(f"  Mean: {errors['mean_translation_error_mm']:.4f} mm")
    
    # Display transformation matrix
    print("\n--- Hand-Eye Transformation Matrix (4x4) ---")
    X = calib_result['X']
    print(X)
    
    print("\n--- Rotation (3x3) ---")
    print(X[:3, :3])
    
    print("\n--- Translation (3x1) ---")
    print(X[:3, 3])
    
    return calib_result


def main():
    """Run all calibration tests."""
    print("\n" + "#"*80)
    print("#" + " "*25 + "CALIBRATION ENGINE TEST" + " "*31 + "#")
    print("#"*80 + "\n")
    
    # Load robot poses from CSV
    csv_path = Path("data/robot_poses.csv")
    
    if not csv_path.exists():
        print(f"❌ Robot poses file not found: {csv_path}")
        return
    
    print(f"Loading robot poses from: {csv_path}")
    robot_poses = load_robot_poses_from_csv(csv_path)
    print(f"✓ Loaded {len(robot_poses)} robot poses\n")
    
    # Test 1: ChArUco detection
    camera_poses, detector, camera_matrix, dist_coeffs = test_charuco_detection()
    
    if len(camera_poses) == 0:
        print("\n❌ No camera poses detected. Cannot proceed with calibration.")
        print("\nPossible reasons:")
        print("  1. ChArUco board parameters don't match the images")
        print("  2. Images don't contain ChArUco boards")
        print("  3. Board is not clearly visible in images")
        return
    
    # Test 2: Hand-eye calibration
    calib_result = test_hand_eye_calibration(robot_poses, camera_poses)
    
    if calib_result is None:
        print("\n❌ Calibration failed")
        return
    
    print("\n" + "="*80)
    print("✓ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80)
    
    # Save result to file
    output_file = Path("data/calibration_result.txt")
    with open(output_file, 'w') as f:
        f.write("Hand-Eye Calibration Result\n")
        f.write("="*80 + "\n\n")
        f.write("Transformation Matrix (4x4):\n")
        f.write(str(calib_result['X']) + "\n\n")
        f.write(f"Method: {calib_result['method_name']}\n")
        f.write(f"Poses used: {calib_result['num_poses_used']}\n")
    
    print(f"\n✓ Results saved to: {output_file}")


if __name__ == "__main__":
    main()
