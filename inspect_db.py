import sqlite3
import json

db = sqlite3.connect("backend/handeye_calib.db")
c = db.cursor()

c.execute("SELECT id, name, csv_filename, status, reprojection_error, transformation_matrix FROM calibration_runs ORDER BY id DESC LIMIT 1")
run = c.fetchone()
print(f"Latest Run: ID={run[0]}, Name={run[1]}, File={run[2]}, Error={run[4]}")

c.execute("SELECT pose_index, x, y, z, rx, ry, rz FROM robot_poses WHERE calibration_run_id = ? ORDER BY pose_index LIMIT 5", (run[0],))
poses = c.fetchall()
print("First 5 poses (X, Y, Z, Rx, Ry, Rz):")
for p in poses:
    print(p)

db.close()
