"""
Test script to verify all API endpoints work correctly.
Tests the complete calibration workflow from authentication to execution.
"""
import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:8000"

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")

def test_authentication():
    """Test authentication endpoint"""
    print_section("TEST 1: Authentication")
    
    # Login
    response = requests.post(
        f"{BASE_URL}/api/v1/token",
        data={"username": "admin", "password": "admin123"}
    )
    
    assert response.status_code == 200, f"Login failed: {response.status_code}"
    data = response.json()
    assert "access_token" in data, "No access token in response"
    assert "token_type" in data, "No token type in response"
    
    print(f"✓ Login successful")
    print(f"  Token type: {data['token_type']}")
    print(f"  Token: {data['access_token'][:50]}...")
    
    return data["access_token"]

def test_get_current_user(token):
    """Test getting current user info"""
    print_section("TEST 2: Get Current User")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/users/me", headers=headers)
    
    assert response.status_code == 200, f"Get user failed: {response.status_code}"
    user = response.json()
    
    print(f"✓ User retrieved")
    print(f"  Username: {user['username']}")
    print(f"  Email: {user['email']}")
    print(f"  Role: {user['role']}")
    
    return user

def test_create_calibration(token):
    """Test creating a calibration"""
    print_section("TEST 3: Create Calibration")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    calibration_data = {
        "name": "Test Calibration API",
        "description": "Automated test calibration",
        "charuco_squares_x": 7,
        "charuco_squares_y": 5,
        "charuco_square_length": 100.0,
        "charuco_marker_length": 75.0,
        "charuco_dictionary": "DICT_5X5_100"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/calibrations",
        headers=headers,
        json=calibration_data
    )
    
    assert response.status_code == 201, f"Create calibration failed: {response.status_code} - {response.text}"
    calibration = response.json()
    
    print(f"✓ Calibration created")
    print(f"  ID: {calibration['id']}")
    print(f"  Name: {calibration['name']}")
    print(f"  Status: {calibration['status']}")
    print(f"  ChArUco: {calibration['charuco_squares_x']}x{calibration['charuco_squares_y']}")
    
    return calibration

def test_list_calibrations(token):
    """Test listing calibrations"""
    print_section("TEST 4: List Calibrations")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/v1/calibrations", headers=headers)
    
    assert response.status_code == 200, f"List calibrations failed: {response.status_code}"
    calibrations = response.json()
    
    print(f"✓ Calibrations retrieved")
    print(f"  Total: {len(calibrations)}")
    for cal in calibrations[-3:]:  # Show last 3
        print(f"  - [{cal['id']}] {cal['name']} ({cal['status']})")
    
    return calibrations

def test_upload_images(token, calibration_id):
    """Test uploading images"""
    print_section("TEST 5: Upload Images")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Check if example images exist
    images_dir = Path("data/examples")
    if not images_dir.exists():
        print("⚠ No example images found, skipping upload test")
        return False
    
    image_files = list(images_dir.glob("*.png"))[:3]  # Upload first 3
    
    if not image_files:
        print("⚠ No PNG images found, skipping upload test")
        return False
    
    files = []
    for img_path in image_files:
        files.append(('files', (img_path.name, open(img_path, 'rb'), 'image/png')))
    
    response = requests.post(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}/upload-images",
        headers=headers,
        files=files
    )
    
    # Close files
    for _, (_, file_obj, _) in files:
        file_obj.close()
    
    assert response.status_code == 200, f"Upload images failed: {response.status_code} - {response.text}"
    result = response.json()
    
    print(f"✓ Images uploaded")
    print(f"  Uploaded: {result['images_uploaded']}")
    print(f"  Files: {', '.join(result['filenames'])}")
    if result['errors']:
        print(f"  Errors: {result['errors']}")
    
    return True

def test_import_poses_csv(token, calibration_id):
    """Test importing robot poses from CSV"""
    print_section("TEST 6: Import Robot Poses (CSV)")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    csv_path = Path("data/robot_poses.csv")
    if not csv_path.exists():
        print("⚠ robot_poses.csv not found, skipping")
        return False
    
    with open(csv_path, 'rb') as f:
        files = {'file': ('robot_poses.csv', f, 'text/csv')}
        response = requests.post(
            f"{BASE_URL}/api/v1/calibrations/{calibration_id}/import-robot-poses-csv",
            headers=headers,
            files=files
        )
    
    assert response.status_code == 200, f"Import CSV failed: {response.status_code} - {response.text}"
    result = response.json()
    
    print(f"✓ CSV imported")
    print(f"  Poses imported: {result['poses_imported']}")
    print(f"  Filename: {result['filename']}")
    if result['errors']:
        print(f"  Errors: {result['errors']}")
    
    return True

def test_list_robot_poses(token, calibration_id):
    """Test listing robot poses"""
    print_section("TEST 7: List Robot Poses")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}/robot-poses",
        headers=headers
    )
    
    assert response.status_code == 200, f"List poses failed: {response.status_code}"
    poses = response.json()
    
    print(f"✓ Robot poses retrieved")
    print(f"  Total poses: {len(poses)}")
    if poses:
        print(f"  First pose: X={poses[0]['x']:.2f}, Y={poses[0]['y']:.2f}, Z={poses[0]['z']:.2f}")
    
    return poses

def test_get_calibration_detail(token, calibration_id):
    """Test getting calibration details"""
    print_section("TEST 8: Get Calibration Detail")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}",
        headers=headers
    )
    
    assert response.status_code == 200, f"Get detail failed: {response.status_code}"
    calibration = response.json()
    
    print(f"✓ Calibration details retrieved")
    print(f"  ID: {calibration['id']}")
    print(f"  Name: {calibration['name']}")
    print(f"  Status: {calibration['status']}")
    print(f"  Created: {calibration['created_at']}")
    
    return calibration

def test_add_robot_pose_manual(token, calibration_id):
    """Test adding a robot pose manually"""
    print_section("TEST 9: Add Robot Pose (Manual)")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Add a new pose (index 100)
    pose_data = {
        "pose_index": 100,
        "x": 100.0,
        "y": 200.0,
        "z": 300.0,
        "rx": 0.0,
        "ry": 0.0,
        "rz": 90.0
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}/robot-poses",
        headers=headers,
        json=pose_data
    )
    
    assert response.status_code == 200, f"Add manual pose failed: {response.status_code} - {response.text}"
    pose = response.json()
    
    print(f"✓ Manual pose added")
    print(f"  Index: {pose['pose_index']}")
    print(f"  Input Method: {pose['input_method']}")
    
    return True

def test_list_images(token, calibration_id):
    """Test listing images"""
    print_section("TEST 10: List Images")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}/images",
        headers=headers
    )
    
    assert response.status_code == 200, f"List images failed: {response.status_code}"
    images = response.json()
    
    print(f"✓ Images retrieved")
    print(f"  Total: {len(images)}")
    if images:
        print(f"  First image: {images[0]['original_filename']}")
    
    return True

def test_execute_calibration(token, calibration_id):
    """Test executing calibration"""
    print_section("TEST 11: Execute Calibration")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}/execute",
        headers=headers
    )
    
    # We expect 200 OK even if calibration fails (success=False in body)
    assert response.status_code == 200, f"Execute failed: {response.status_code} - {response.text}"
    result = response.json()
    
    print(f"✓ Execution endpoint called")
    print(f"  Success: {result['success']}")
    if result['success']:
        print(f"  Error (Reprojection): {result['reprojection_error']:.4f}")
    else:
        print(f"  Message: {result.get('error_message')}")
        
    return True

def test_delete_calibration(token, calibration_id):
    """Test deleting calibration"""
    print_section("TEST 12: Delete Calibration")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.delete(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}",
        headers=headers
    )
    
    assert response.status_code == 204, f"Delete failed: {response.status_code} - {response.text}"
    
    # Verify it's gone
    response = requests.get(
        f"{BASE_URL}/api/v1/calibrations/{calibration_id}",
        headers=headers
    )
    assert response.status_code == 404, "Calibration still exists after delete"
    
    print(f"✓ Calibration deleted successfully")
    return True

def main():
    """Run all API tests"""
    print("\n" + "#"*80)
    print("#" + " "*25 + "API ENDPOINTS TEST" + " "*36 + "#")
    print("#"*80 + "\n")
    
    print(f"Testing API at: {BASE_URL}")
    print(f"Documentation: {BASE_URL}/docs\n")
    
    try:
        # Test 1: Authentication
        token = test_authentication()
        
        # Test 2: Get current user
        user = test_get_current_user(token)
        
        # Test 3: Create calibration
        calibration = test_create_calibration(token)
        calibration_id = calibration['id']
        
        # Test 4: List calibrations
        calibrations = test_list_calibrations(token)
        
        # Test 5: Upload images (optional if files exist)
        images_uploaded = test_upload_images(token, calibration_id)
        
        # Test 6: Import poses CSV (optional if file exists)
        poses_imported = test_import_poses_csv(token, calibration_id)
        
        # Test 7: List robot poses
        if poses_imported:
            poses = test_list_robot_poses(token, calibration_id)
            
        # Test 8: Get calibration detail
        detail = test_get_calibration_detail(token, calibration_id)
        
        # Test 9: Add manual pose
        test_add_robot_pose_manual(token, calibration_id)
        
        # Test 10: List images
        if images_uploaded:
            test_list_images(token, calibration_id)
            
        # Test 11: Execute calibration
        # Only try if we have images and poses
        if images_uploaded and poses_imported:
            test_execute_calibration(token, calibration_id)
            
        # Test 12: Delete calibration
        # Create a temporary one to delete so we keep the main one for inspection
        print("\n--- Creating temporary calibration for delete test ---")
        temp_cal = test_create_calibration(token)
        test_delete_calibration(token, temp_cal['id'])
        
        # Summary
        print_section("SUMMARY")
        print(f"✅ All API tests completed successfully!")
        print(f"\nEndpoints tested:")
        print(f"  ✓ POST /api/v1/token")
        print(f"  ✓ GET  /api/v1/users/me")
        print(f"  ✓ POST /api/v1/calibrations")
        print(f"  ✓ GET  /api/v1/calibrations")
        print(f"  ✓ GET  /api/v1/calibrations/{{id}}")
        print(f"  ✓ DELETE /api/v1/calibrations/{{id}}")
        
        if images_uploaded:
            print(f"  ✓ POST /api/v1/calibrations/{{id}}/upload-images")
            print(f"  ✓ GET  /api/v1/calibrations/{{id}}/images")
        if poses_imported:
            print(f"  ✓ POST /api/v1/calibrations/{{id}}/import-robot-poses-csv")
            print(f"  ✓ GET  /api/v1/calibrations/{{id}}/robot-poses")
            print(f"  ✓ POST /api/v1/calibrations/{{id}}/robot-poses (Manual)")
            
        if images_uploaded and poses_imported:
             print(f"  ✓ POST /api/v1/calibrations/{{id}}/execute")
        
        print(f"\n📊 Test calibration created with ID: {calibration_id}")
        print(f"🌐 View in Swagger UI: {BASE_URL}/docs#{'/calibrations' if calibration_id else ''}")
        
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
