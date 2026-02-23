import sqlite3
import numpy as np
import cv2
import json
from scipy.spatial.transform import Rotation as R
from itertools import permutations
import sys

# Connect in read-only mode to avoid locking
try:
    conn = sqlite3.connect('file:handeye_calibration.db?mode=ro', uri=True)
except Exception as e:
    print("Cannot open DB:", e)
    sys.exit(1)

c = conn.cursor()
c.execute('SELECT id FROM calibration_runs ORDER BY id DESC LIMIT 1')
row = c.fetchone()
if not row:
    print("No run found")
    sys.exit(1)
run_id = row[0]

c.execute('SELECT pose_index, x, y, z, rx, ry, rz FROM robot_poses WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
r_poses = c.fetchall()

c.execute('SELECT pose_index, rotation_matrix, translation_vector FROM camera_poses WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
c_poses = c.fetchall()
conn.close()

print(f"Loaded {len(r_poses)} robot poses and {len(c_poses)} camera poses for run {run_id}")

R_target2cam = []
t_target2cam = []
for p in c_poses:
    rm = np.array(json.loads(p[1]))
    tv = np.array(json.loads(p[2])).ravel()
    R_target2cam.append(rm)
    t_target2cam.append(tv)

seqs = ['xyz', 'xyx', 'xzy', 'xzx', 'yzx', 'yzy', 'yxz', 'yxy', 'zxy', 'zxz', 'zyx', 'zyz']
seqs += [s.upper() for s in seqs]
perms = list(permutations([0, 1, 2]))

best_err = float('inf')
best_conf = None

n_loops = 0
for e2h in [False, True]:
    for seq in seqs:
        for p in perms:
            for is_rad in [False, True]:
                for trans_scale in [1.0, 1000.0, 0.001]:
                    n_loops += 1
                    if n_loops % 50 == 0:
                        print(f"Loop {n_loops}/1728...", flush=True)
                    R_g2b = []
                    t_g2b = []
                    for rp in r_poses:
                        x, y, z, rx, ry, rz = rp[1:7]
                        angles = [rx, ry, rz]
                        
                        try:
                            rot = R.from_euler(seq, [angles[p[0]], angles[p[1]], angles[p[2]]], degrees=not is_rad)
                            Rmat = rot.as_matrix()
                            tvec = np.array([x, y, z]) / trans_scale
                            
                            if e2h:
                                Rmat = Rmat.T
                                tvec = -Rmat @ tvec
                                
                            R_g2b.append(Rmat)
                            t_g2b.append(tvec)
                        except Exception as e:
                            break
                    
                    if len(R_g2b) == len(R_target2cam):
                        try:
                            R_HE, t_HE = cv2.calibrateHandEye(R_g2b, t_g2b, R_target2cam, t_target2cam)
                            errs = []
                            X = np.eye(4)
                            X[:3,:3] = R_HE
                            X[:3,3] = t_HE.ravel()
                            
                            for A_R, A_t, B_R, B_t in zip(R_g2b, t_g2b, R_target2cam, t_target2cam):
                                A = np.eye(4)
                                A[:3,:3] = A_R
                                A[:3,3] = A_t.ravel()
                                B = np.eye(4)
                                B[:3,:3] = B_R
                                B[:3,3] = B_t.ravel()
                                T = A @ X @ B
                                errs.append(T[:3,3])
                            
                            errs = np.array(errs)
                            mean_t = np.mean(errs, axis=0)
                            std_err = np.mean(np.linalg.norm(errs - mean_t, axis=1))
                            
                            if std_err < best_err:
                                best_err = std_err
                                best_conf = (e2h, seq, p, is_rad, trans_scale)
                                print(f"NEW BEST! Err={std_err:.2f}mm, Eye2Hand={e2h}, Seq={seq}, Perm={p}, Rad={is_rad}, Scale={trans_scale}", flush=True)
                        except Exception as e:
                            pass

print("BEST CONFIG:", best_conf, "with error:", best_err)
