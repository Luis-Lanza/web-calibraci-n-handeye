def calibrate_eye_hand(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, eye_to_hand=False):

    if eye_to_hand:
        # change coordinates from gripper2base to base2gripper
        R_base2gripper, t_base2gripper = [], []
        for R, t in zip(R_gripper2base, t_gripper2base):
            R_b2g = R.T
            t_b2g = -R_b2g @ t
            R_base2gripper.append(R_b2g)
            t_base2gripper.append(t_b2g)
        
        # change parameters values
        R_gripper2base = R_base2gripper
        t_gripper2base = t_base2gripper

    # calibrate
    R, t = cv2.calibrateHandEye(
        R_gripper2base=R_gripper2base,
        t_gripper2base=t_gripper2base,
        R_target2cam=R_target2cam,
        t_target2cam=t_target2cam,
    )

    return R, t

if __name__ == "__main__":
    import csv
    import numpy as np
    import os
    import cv2
    from scipy.spatial.transform import Rotation as R

    # Paths
    target2cam_csv = os.path.join('data', 'cam2target_matrices.csv')
    gripper2base_csv = os.path.join('data', 'gripper2base_matrices.csv')
    output_csv = os.path.join('data', 'cam2base_matrix.csv')

    # Leer matrices cam2target
    R_target2cam = []
    t_target2cam = []
    with open(target2cam_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Rmat = np.array([
                [float(row['m0']), float(row['m1']), float(row['m2'])],
                [float(row['m4']), float(row['m5']), float(row['m6'])],
                [float(row['m8']), float(row['m9']), float(row['m10'])]
            ])  
            tvec = np.array([float(row['m3']), float(row['m7']), float(row['m11'])])
            R_target2cam.append(Rmat)
            t_target2cam.append(tvec)

    # Leer matrices gripper2base
    R_gripper2base = []
    t_gripper2base = []
    with open(gripper2base_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Rmat = np.array([
                [float(row['m0']), float(row['m1']), float(row['m2'])],
                [float(row['m4']), float(row['m5']), float(row['m6'])],
                [float(row['m8']), float(row['m9']), float(row['m10'])]
            ])
            tvec = np.array([float(row['m3']), float(row['m7']), float(row['m11'])])
            R_gripper2base.append(Rmat)
            t_gripper2base.append(tvec)

    # Convertir a np.array
    R_gripper2base = np.array(R_gripper2base)
    t_gripper2base = np.array(t_gripper2base)
    R_target2cam = np.array(R_target2cam)
    t_target2cam = np.array(t_target2cam)
    
    R, t = calibrate_eye_hand(R_gripper2base, t_gripper2base, R_target2cam, t_target2cam, eye_to_hand=False)
    print("R:", R)
    print("t:", t)
