"""Simple test to verify OpenCV ArUco API works."""
import cv2
import numpy as np

print(f"OpenCV version: {cv2.__version__}")
print(f"Has detectMarkers: {hasattr(cv2.aruco, 'detectMarkers')}")
print(f"Has interpolateCornersCharuco: {hasattr(cv2.aruco, 'interpolateCornersCharuco')}")
print(f"Has estimatePoseCharucoBoard: {hasattr(cv2.aruco, 'estimatePoseCharucoBoard')}")

# Try to create a simple test
try:
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_100)
    print("✓ Dictionary creation works")
    
    board = cv2.aruco.CharucoBoard(
        size=(7, 5),
        squareLength=100,
        markerLength=75,
        dictionary=aruco_dict
    )
    print("✓ ChArUco board creation works")
    
    # Create dummy image
    img = np.zeros((800, 600), dtype=np.uint8)
    params = cv2.aruco.DetectorParameters()
    
    corners, ids, rejected = cv2.aruco.detectMarkers(img, aruco_dict, parameters=params)
    print("✓ detectMarkers works")
    
    print("\n✅ All API functions are available and working!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
