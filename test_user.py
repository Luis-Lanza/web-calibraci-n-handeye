import sqlite3
import numpy as np
import cv2
import json

def calculate_reprojection_error(X, R_g2b, t_g2b, R_t2c, t_t2c):
    errs = []
    for A_R, A_t, B_R, B_t in zip(R_g2b, t_g2b, R_t2c, t_t2c):
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
    return std_err

def test_db():
    conn = sqlite3.connect('copy_test.db', uri=True)
    c = conn.cursor()
    c.execute('SELECT id FROM calibration_runs ORDER BY id DESC LIMIT 1')
    run_id = c.fetchone()[0]

    c.execute('SELECT pose_index, rotation_matrix, translation_vector FROM robot_poses WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
    r_poses = c.fetchall()

    c.execute('SELECT pose_index, rotation_matrix, translation_vector FROM camera_poses WHERE calibration_run_id=? ORDER BY pose_index', (run_id,))
    c_poses = c.fetchall()
    conn.close()

    R_g2b, t_g2b = [], []
    for p in r_poses:
        R_g2b.append(np.array(json.loads(p[1])))
        t_g2b.append(np.array(json.loads(p[2])).ravel())

    R_target2cam, t_target2cam = [], []
    for p in c_poses:
        R_target2cam.append(np.array(json.loads(p[1])))
        t_target2cam.append(np.array(json.loads(p[2])).ravel())
    
    R, t = cv2.calibrateHandEye(R_g2b, t_g2b, R_target2cam, t_target2cam)
    X = np.eye(4)
    X[:3,:3] = R
    X[:3,3] = t.ravel()
    
    err = calculate_reprojection_error(X, R_g2b, t_g2b, R_target2cam, t_target2cam)
    print("Normal DB Error:", err)

if __name__ == '__main__':
    test_db()
