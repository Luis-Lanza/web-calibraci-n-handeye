import reflex as rx
from typing import List, Dict, Any, Optional
from ...services.api_client import APIClient
from ...state import AuthState

class CalibrationState(AuthState):
    """State for the calibration wizard."""
    current_calibration_id: int = 0
    calibration: Dict[str, Any] = {}
    images: List[Dict[str, Any]] = []
    poses: List[Dict[str, Any]] = []
    active_step: int = 0
    
    # Create Form
    new_cal_name: str = ""
    new_cal_desc: str = ""
    squares_x: int = 7
    squares_y: int = 5
    square_len: float = 100.0
    marker_len: float = 75.0
    
    def set_new_cal_name(self, value: str):
        self.new_cal_name = value
        
    def set_new_cal_desc(self, value: str):
        self.new_cal_desc = value
        
    def set_squares_x(self, value: str):
        try:
            self.squares_x = int(value)
        except ValueError:
            pass
            
    def set_squares_y(self, value: str):
        try:
            self.squares_y = int(value)
        except ValueError:
            pass
            
    def set_square_len(self, value: str):
        try:
            self.square_len = float(value)
        except ValueError:
            pass
            
    def set_marker_len(self, value: str):
        try:
            self.marker_len = float(value)
        except ValueError:
            pass
    
    async def create_calibration(self):
        """Create a new calibration run."""
        data = {
            "name": self.new_cal_name,
            "description": self.new_cal_desc,
            "charuco_squares_x": self.squares_x,
            "charuco_squares_y": self.squares_y,
            "charuco_square_length": self.square_len,
            "charuco_marker_length": self.marker_len,
            "charuco_dictionary": "DICT_5X5_100"
        }
        
        response = await APIClient.post("/calibrations", json_data=data, token=self.token)
        
        if response.status_code == 201:
            cal = response.json()
            self.current_calibration_id = cal["id"]
            return rx.redirect(f"/calibration/{cal['id']}/images")
        else:
            return rx.window_alert("Error al crear calibración")

    async def load_calibration(self):
        """Load calibration data by ID."""
        # Get ID from URL params (handled by page load)
        # In Reflex, route args are available in self.router.page.params
        # But for now let's rely on the state variable being set or passed
        
        # We need to get the ID from the router if it's not set
        # This is a bit tricky in async load. 
        # Let's assume for now we use the one in state if set.
        
        if not self.current_calibration_id:
            # Try to get from router params if possible, or it might be passed as arg to on_load
            pass
            
        response = await APIClient.get(f"/calibrations/{self.current_calibration_id}", token=self.token)
        if response.status_code == 200:
            self.calibration = response.json()
        
        # Load images
        img_resp = await APIClient.get(f"/calibrations/{self.current_calibration_id}/images", token=self.token)
        if img_resp.status_code == 200:
            self.images = img_resp.json()
            
        # Load poses
        pose_resp = await APIClient.get(f"/calibrations/{self.current_calibration_id}/robot-poses", token=self.token)
        if pose_resp.status_code == 200:
            self.poses = pose_resp.json()

    async def upload_files(self, files: List[rx.UploadFile]):
        """Upload selected files."""
        if not files:
            return
            
        # Prepare files for upload
        # Note: Reflex handles file uploads differently, we need to read the file content
        # and send it via APIClient. But APIClient expects a dict of files.
        # Since Reflex upload handling is complex with async, we might need a simpler approach
        # or use the backend upload handler directly if possible.
        
        # For now, let's assume we can send them one by one or in batch
        # This part requires careful implementation with Reflex's upload component
        
        upload_data = []
        for file in files:
            content = await file.read()
            upload_data.append(("files", (file.filename, content, file.content_type)))
            
        response = await APIClient.post_files(
            f"/calibrations/{self.current_calibration_id}/upload-images",
            files=upload_data,
            token=self.token
        )
        
        if response.status_code == 200:
            await self.load_calibration()
            return rx.window_alert("Imágenes subidas correctamente")
        else:
            return rx.window_alert("Error al subir imágenes")

    async def upload_csv(self, files: List[rx.UploadFile]):
        """Upload CSV file."""
        if not files:
            return
            
        file = files[0]
        content = await file.read()
        
        response = await APIClient.post_files(
            f"/calibrations/{self.current_calibration_id}/import-robot-poses-csv",
            files={"file": (file.filename, content, file.content_type)},
            token=self.token
        )
        
        if response.status_code == 200:
            await self.load_calibration()
            return rx.window_alert("Poses importadas correctamente")
        else:
            return rx.window_alert("Error al importar CSV")

    async def run_calibration(self):
        """Execute calibration process."""
        response = await APIClient.post(f"/calibrations/{self.current_calibration_id}/execute", token=self.token)
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                await self.load_calibration()
                return rx.redirect(f"/calibration/{self.current_calibration_id}/results")
            else:
                return rx.window_alert(f"Error: {result.get('error_message')}")
        else:
            return rx.window_alert("Error de servidor al ejecutar calibración")
