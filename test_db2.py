import sqlite3

try:
    conn = sqlite3.connect('temp.db', timeout=2.0)
    c = conn.cursor()
    c.execute('SELECT pose_index, x, y, z FROM robot_poses ORDER BY calibration_run_id DESC, pose_index ASC LIMIT 5;')
    robot = c.fetchall()
    print("ROBOT POSES (x,y,z):", robot)
    
    c.execute('SELECT pose_index, translation_vector FROM camera_poses ORDER BY calibration_run_id DESC, pose_index ASC LIMIT 5;')
    cam = c.fetchall()
    print("CAMERA POSES (translation):", cam)
    conn.close()
except Exception as e:
    print("ERROR:", e)
