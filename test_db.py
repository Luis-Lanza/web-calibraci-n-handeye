from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.calibration import CalibrationRun, RobotPose, CameraPose

engine = create_engine('sqlite:///handeye_calibration.db')
Session = sessionmaker(bind=engine)
db = Session()

run = db.query(CalibrationRun).order_by(CalibrationRun.id.desc()).first()
if not run:
    print("No runs found")
else:
    print(f"Run {run.id}: name={run.name}")
    print("Robot Poses (first 3):")
    for rp in db.query(RobotPose).filter_by(calibration_run_id=run.id).order_by(RobotPose.pose_index).limit(3):
        print(f"  {rp.pose_index}: x={rp.x}, y={rp.y}, z={rp.z}")
    
    print("Camera Poses (first 3):")
    for cp in db.query(CameraPose).filter_by(calibration_run_id=run.id).order_by(CameraPose.pose_index).limit(3):
        try:
            t = cp.translation_vector
            print(f"  {cp.pose_index}: x={t[0]}, y={t[1]}, z={t[2]}")
        except:
            print(f"  {cp.pose_index}: Error parsing json")

db.close()
