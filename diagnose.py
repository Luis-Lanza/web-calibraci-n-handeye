"""
Diagnostic v3: Only brute force with DB camera poses.
Also re-estimate using CharucoDetector + solvePnP (same as backend but with cv2.Rodrigues).
"""
import sqlite3
import numpy as np
import cv2
import json
import os
from scipy.spatial.transform import Rotation as R
from itertools import permutations

conn = sqlite3.connect('handeye_calibration.db')
c = conn.cursor()
c.execute('SELECT id FROM calibration_runs ORDER BY id DESC LIMIT 1')
run_id = c.fetchone()[0]

c.execute('''SELECT charuco_squares_x, charuco_squares_y, charuco_square_length, 
             charuco_marker_length, charuco_dictionary,
             camera_fx, camera_fy, camera_cx, camera_cy,
             camera_k1, camera_k2, camera_p1, camera_p2, camera_k3
             FROM calibration_runs WHERE id=?''', (run_id,))
params = c.fetchone()
sq_x, sq_y, sq_len, mk_len, dict_name = params[:5]
fx, fy, cx, cy = params[5:9]

c.execute('SELECT pose_index, x, y, z, rx, ry, rz FROM robot_poses WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
robot_euler = c.fetchall()

c.execute('SELECT pose_index, rotation_matrix, translation_vector FROM camera_poses WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
cam_poses_db = c.fetchall()

c.execute('SELECT pose_index, image_path FROM calibration_images WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
images = c.fetchall()
conn.close()

print(f"=== Run {run_id}: fx={fx}, fy={fy} ===")
print(f"Robot: {len(robot_euler)}, CamDB: {len(cam_poses_db)}, Imgs: {len(images)}")

camera_matrix = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]], dtype=np.float64)
dist_coeffs = np.zeros(5, dtype=np.float64)

# Re-estimate camera poses using CharucoDetector (fully modern API)
dict_id = getattr(cv2.aruco, dict_name)
aruco_dict = cv2.aruco.getPredefinedDictionary(dict_id)
board = cv2.aruco.CharucoBoard(
    size=(sq_x, sq_y), squareLength=sq_len, markerLength=mk_len, dictionary=aruco_dict
)
charuco_det = cv2.aruco.CharucoDetector(board)

R_t2c_re = []
t_t2c_re = []

print("\n=== Re-estimating camera poses with CharucoDetector + solvePnP ===")
for img_info in images:
    idx = img_info[0]
    img_path = img_info[1]
    if not os.path.exists(img_path):
        continue
    img = cv2.imread(img_path)
    charuco_corners, charuco_ids, _, _ = charuco_det.detectBoard(img)
    
    if charuco_corners is not None and len(charuco_corners) > 3:
        obj_points = board.getChessboardCorners()
        detected_ids = charuco_ids.flatten()
        detected_corners = charuco_corners.reshape(-1, 2)
        
        obj_pts = []
        img_pts = []
        for i, cid in enumerate(detected_ids):
            if cid < len(obj_points):
                obj_pts.append(obj_points[cid])
                img_pts.append(detected_corners[i])
        
        obj_pts = np.array(obj_pts, dtype=np.float32)
        img_pts = np.array(img_pts, dtype=np.float32)
        
        success, rvec, tvec = cv2.solvePnP(obj_pts, img_pts, camera_matrix, dist_coeffs)
        if success:
            Rmat, _ = cv2.Rodrigues(rvec)
            R_t2c_re.append(Rmat)
            t_t2c_re.append(tvec.flatten())

# Load DB camera poses
R_t2c_db = [np.array(json.loads(cp[1])) for cp in cam_poses_db]
t_t2c_db = [np.array(json.loads(cp[2])).ravel() for cp in cam_poses_db]

print(f"Re-estimated: {len(R_t2c_re)}, DB: {len(R_t2c_db)}")

# Compare
if len(R_t2c_re) > 0 and len(R_t2c_db) > 0:
    print(f"\nPose 1 - Re-est t: {t_t2c_re[0]}")
    print(f"Pose 1 - DB     t: {t_t2c_db[0]}")
    print(f"t diff: {np.linalg.norm(t_t2c_re[0] - t_t2c_db[0]):.4f}mm")
    print(f"R diff: {np.linalg.norm(R_t2c_re[0] - R_t2c_db[0], 'fro'):.6f}")

# ============================================================
# Brute force
# ============================================================
def run_calib(R_g2b, t_g2b, R_t2c, t_t2c):
    try:
        R_HE, t_HE = cv2.calibrateHandEye(R_g2b, t_g2b, R_t2c, t_t2c)
        X = np.eye(4); X[:3,:3] = R_HE; X[:3,3] = t_HE.ravel()
        errs = []
        for AR, At, BR, Bt in zip(R_g2b, t_g2b, R_t2c, t_t2c):
            A = np.eye(4); A[:3,:3] = AR; A[:3,3] = At.ravel()
            B = np.eye(4); B[:3,:3] = BR; B[:3,3] = Bt.ravel()
            T = A @ X @ B
            errs.append(T[:3,3])
        errs = np.array(errs)
        mean_t = np.mean(errs, axis=0)
        return np.mean(np.linalg.norm(errs - mean_t, axis=1)), X
    except:
        return float('inf'), None

seqs = ['xyz', 'xzy', 'yzx', 'yxz', 'zxy', 'zyx']
seqs += [s.upper() for s in seqs]
perms = list(permutations([0, 1, 2]))

for cam_label, R_cam, t_cam in [("RE-ESTIMATED", R_t2c_re, t_t2c_re), 
                                  ("DB", R_t2c_db, t_t2c_db)]:
    if len(R_cam) == 0:
        continue
    print(f"\n{'='*50}")
    print(f" {cam_label} camera poses ({len(R_cam)} poses)")
    print(f"{'='*50}")
    
    top = []
    for e2h in [False, True]:
        for seq in seqs:
            for p in perms:
                R_g2b, t_g2b = [], []
                for rp in robot_euler:
                    x, y, z, rx, ry, rz = rp[1:7]
                    angles = [rx, ry, rz]
                    try:
                        rot = R.from_euler(seq, [angles[p[0]], angles[p[1]], angles[p[2]]], degrees=True)
                        Rmat = rot.as_matrix()
                        tvec = np.array([x, y, z])
                        if e2h:
                            Rmat = Rmat.T
                            tvec = -Rmat @ tvec
                        R_g2b.append(Rmat)
                        t_g2b.append(tvec)
                    except:
                        break
                
                if len(R_g2b) == len(R_cam):
                    err, X = run_calib(R_g2b, t_g2b, R_cam, t_cam)
                    top.append((err, e2h, seq, p))
    
    top.sort()
    print(f"\n  TOP 10:")
    for err, e2h, seq, p in top[:10]:
        print(f"    Err={err:.2f}mm, e2h={e2h}, seq={seq}, perm={p}")

print("\n=== DONE ===")
