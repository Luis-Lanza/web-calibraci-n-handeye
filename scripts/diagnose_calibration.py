"""
Diagnostic script to inspect calibration data and check for unit/format issues.
"""
import sqlite3
import os
import json
import numpy as np

# Get the database path
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
db_path = os.path.join(backend_dir, "handeye_calibration.db")

if not os.path.exists(db_path):
    db_path = os.path.join(os.path.dirname(__file__), "..", "handeye_calibration.db")

print(f"📊 Connecting to database: {db_path}")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get latest calibration
cursor.execute("SELECT * FROM calibration_runs ORDER BY id DESC LIMIT 1")
calib = cursor.fetchone()

if not calib:
    print("❌ No calibration found")
    exit()

print(f"\n🔍 Analyzing Calibration ID: {calib['id']}")
print(f"Name: {calib['name']}")
print(f"Status: {calib['status']}")
print(f"Reprojection Error: {calib['reprojection_error']}")
print(f"Translation Error: {calib['translation_error_mm']}")
print(f"Rotation Error: {calib['rotation_error_deg']}")

# Get Robot Poses
cursor.execute("SELECT * FROM robot_poses WHERE calibration_run_id = ? ORDER BY pose_index", (calib['id'],))
robot_poses = cursor.fetchall()

print(f"\n🤖 Robot Poses ({len(robot_poses)}):")
xs, ys, zs = [], [], []
rxs, rys, rzs = [], [], []

for pose in robot_poses:
    xs.append(pose['x'])
    ys.append(pose['y'])
    zs.append(pose['z'])
    rxs.append(pose['rx'])
    rys.append(pose['ry'])
    rzs.append(pose['rz'])

print(f"  X range: {min(xs):.4f} to {max(xs):.4f}")
print(f"  Y range: {min(ys):.4f} to {max(ys):.4f}")
print(f"  Z range: {min(zs):.4f} to {max(zs):.4f}")
print(f"  Rx range: {min(rxs):.4f} to {max(rxs):.4f}")
print(f"  Ry range: {min(rys):.4f} to {max(rys):.4f}")
print(f"  Rz range: {min(rzs):.4f} to {max(rzs):.4f}")

# Check for meters vs mm
max_trans = max(max(abs(x) for x in xs), max(abs(y) for y in ys), max(abs(z) for z in zs))
if max_trans < 10.0:
    print("\n⚠️  WARNING: Robot translation values are very small (< 10.0).")
    print("    Likely in METERS. System expects MILLIMETERS.")
else:
    print("\n✅ Robot translation values look like MM (> 10.0).")

# Check for radians vs degrees
max_rot = max(max(abs(x) for x in rxs), max(abs(y) for y in rys), max(abs(z) for z in rzs))
if max_rot < 7.0: # 2*pi is ~6.28
    print("\n⚠️  WARNING: Robot rotation values are small (< 7.0).")
    print("    Likely in RADIANS. System expects DEGREES.")
else:
    print("\n✅ Robot rotation values look like DEGREES (> 7.0).")

# Get Camera Poses (computed)
cursor.execute("SELECT * FROM camera_poses WHERE calibration_run_id = ? ORDER BY pose_index", (calib['id'],))
camera_poses = cursor.fetchall()

print(f"\n📷 Camera Poses ({len(camera_poses)}):")
if len(camera_poses) > 0:
    # Parse JSON translation vector
    t_cam = json.loads(camera_poses[0]['translation_vector'])
    print(f"  Sample T (Pose 1): {t_cam}")
    
    # Check camera units
    cam_trans_mag = np.linalg.norm(t_cam)
    print(f"  Sample T Magnitude: {cam_trans_mag:.2f}")
    
    if cam_trans_mag < 10.0:
        print("  ⚠️  Camera translation seems to be in METERS (or very close).")
    else:
        print("  ✅ Camera translation seems to be in MM.")

# ============================================================================
# Test Calibration with Different Rotation Formats
# ============================================================================
print("\n🧪 Testing Rotation Formats...")

import cv2
from scipy.spatial.transform import Rotation as R

def get_matrix(pose, fmt):
    x, y, z = pose['x'], pose['y'], pose['z']
    rx, ry, rz = pose['rx'], pose['ry'], pose['rz']
    
    t = np.array([x, y, z])
    
    if fmt == 'euler_xyz':
        r = R.from_euler('xyz', [rx, ry, rz], degrees=True)
    elif fmt == 'euler_zyx':
        # KUKA A,B,C is Z,Y,X. 
        # If mapped A->rx, B->ry, C->rz, then rx=Z, ry=Y, rz=X
        # So we want rotation order z,y,x with angles rx,ry,rz
        r = R.from_euler('zyx', [rx, ry, rz], degrees=True)
    elif fmt == 'rot_vec':
        # Rotation vector (magnitude is angle in radians usually, but here maybe degrees?)
        # If degrees=True in user input, we might need to convert magnitude to radians
        vec = np.array([rx, ry, rz])
        mag = np.linalg.norm(vec)
        if mag > 0:
            # Assume vector is in degrees (magnitude is degrees)
            # Convert to radians for scipy
            vec_rad = vec * (np.pi / 180.0)
            r = R.from_rotvec(vec_rad)
        else:
            r = R.identity()
    elif fmt == 'rot_vec_rad':
        # Assume already radians
        r = R.from_rotvec(np.array([rx, ry, rz]))
        
    mat = np.eye(4)
    mat[:3, :3] = r.as_matrix()
    mat[:3, 3] = t
    return mat

def solve_calib(robot_matrices, camera_matrices):
    R_gripper2base = [m[:3, :3] for m in robot_matrices]
    t_gripper2base = [m[:3, 3] for m in robot_matrices]
    R_target2cam = [m[:3, :3] for m in camera_matrices]
    t_target2cam = [m[:3, 3] for m in camera_matrices]
    
    try:
        R_cam2gripper, t_cam2gripper = cv2.calibrateHandEye(
            R_gripper2base, t_gripper2base,
            R_target2cam, t_target2cam,
            method=cv2.CALIB_HAND_EYE_TSAI
        )
        
        X = np.eye(4)
        X[:3, :3] = R_cam2gripper
        X[:3, 3] = t_cam2gripper.ravel()
        
        # Calculate error (consistency)
        errors = []
        for A, B in zip(robot_matrices, camera_matrices):
            # T_target_base = A * X * B
            T = A @ X @ B
            errors.append(T[:3, 3])
        
        mean_t = np.mean(errors, axis=0)
        trans_errors = [np.linalg.norm(t - mean_t) for t in errors]
        return np.mean(trans_errors)
        
    except Exception as e:
        return float('inf')

# Prepare camera matrices
cam_mats = []
for cp in camera_poses:
    rm = np.array(json.loads(cp['rotation_matrix']))
    tv = np.array(json.loads(cp['translation_vector']))
    m = np.eye(4)
    m[:3, :3] = rm
    m[:3, 3] = tv
    cam_mats.append(m)

formats = ['euler_xyz', 'euler_zyx', 'rot_vec', 'rot_vec_rad']

for fmt in formats:
    rob_mats = [get_matrix(p, fmt) for p in robot_poses]
    if len(rob_mats) == len(cam_mats) and len(rob_mats) > 2:
        error = solve_calib(rob_mats, cam_mats)
        print(f"  Format {fmt:15s}: Error = {error:.2f} mm")
    else:
        print(f"  Format {fmt:15s}: Not enough data")


print("\n🧪 Testing Configurations (Inversions)...")

def invert_matrix(M):
    R = M[:3, :3]
    t = M[:3, 3]
    Minv = np.eye(4)
    Minv[:3, :3] = R.T
    Minv[:3, 3] = -R.T @ t
    return Minv

# Base matrices (using Euler XYZ as it was close-ish)
base_rob_mats = [get_matrix(p, 'euler_xyz') for p in robot_poses]
base_cam_mats = cam_mats

configs = [
    ("Standard (Eye-in-Hand)", base_rob_mats, base_cam_mats),
    ("Inverted Robot (Eye-to-Hand?)", [invert_matrix(m) for m in base_rob_mats], base_cam_mats),
    ("Inverted Camera", base_rob_mats, [invert_matrix(m) for m in base_cam_mats]),
    ("Both Inverted", [invert_matrix(m) for m in base_rob_mats], [invert_matrix(m) for m in base_cam_mats]),
]

for name, robs, cams in configs:
    if len(robs) == len(cams) and len(robs) > 2:
        error = solve_calib(robs, cams)
        print(f"  Config {name:30s}: Error = {error:.2f} mm")

print("\n🧪 Testing KUKA Format (Euler ZYX) with Inversions...")
kuka_rob_mats = [get_matrix(p, 'euler_zyx') for p in robot_poses]

configs_kuka = [
    ("KUKA Standard", kuka_rob_mats, base_cam_mats),
    ("KUKA Inv Robot", [invert_matrix(m) for m in kuka_rob_mats], base_cam_mats),
    ("KUKA Inv Cam", kuka_rob_mats, [invert_matrix(m) for m in base_cam_mats]),
]

for name, robs, cams in configs_kuka:
    if len(robs) == len(cams) and len(robs) > 2:
        error = solve_calib(robs, cams)
        print(f"  Config {name:30s}: Error = {error:.2f} mm")

print("\n📏 Checking Scale Factor (Relative Motion)...")

def get_relative_translations(matrices):
    trans_mags = []
    for i in range(len(matrices) - 1):
        # Rel transform T_i^{-1} * T_{i+1}
        T1 = matrices[i]
        T2 = matrices[i+1]
        T_rel = np.linalg.inv(T1) @ T2
        mag = np.linalg.norm(T_rel[:3, 3])
        trans_mags.append(mag)
    return np.array(trans_mags)

rob_mags = get_relative_translations(base_rob_mats)
cam_mags = get_relative_translations(base_cam_mats)

print(f"  Robot Relative Motions (mm): {rob_mags}")
print(f"  Camera Relative Motions (mm): {cam_mags}")

if len(rob_mags) > 0 and len(cam_mags) > 0:
    ratios = rob_mags / (cam_mags + 1e-6) # Avoid div by zero
    avg_ratio = np.mean(ratios)
    median_ratio = np.median(ratios)
    
    print(f"  Ratio (Robot / Camera): Mean={avg_ratio:.4f}, Median={median_ratio:.4f}")
    
    if 0.9 < median_ratio < 1.1:
        print("  ✅ Scale looks correct (Ratio ~ 1.0)")
    elif 900 < median_ratio < 1100:
        print("  ⚠️  Scale mismatch: Robot is in MM, Camera is in METERS? (Ratio ~ 1000)")
    elif 0.0009 < median_ratio < 0.0011:
        print("  ⚠️  Scale mismatch: Robot is in METERS, Camera is in MM? (Ratio ~ 0.001)")
    else:
        print(f"  ⚠️  Scale mismatch detected. Factor: {median_ratio:.4f}")
        print("      Possible causes: Wrong ChArUco square size, or unsynchronized data.")

    # Try to solve with scaled camera poses
    print(f"\n🧪 Testing with Scale Factor {median_ratio:.4f}...")
    
    scaled_cam_mats = []
    for m in base_cam_mats:
        m_scaled = m.copy()
        m_scaled[:3, 3] *= median_ratio
        scaled_cam_mats.append(m_scaled)
    
    error_scaled = solve_calib(base_rob_mats, scaled_cam_mats)
    print(f"  Scaled Standard: Error = {error_scaled:.2f} mm")
    
    # Try scaled with KUKA
    error_scaled_kuka = solve_calib(kuka_rob_mats, scaled_cam_mats)
    print(f"  Scaled KUKA: Error = {error_scaled_kuka:.2f} mm")

conn.close()
