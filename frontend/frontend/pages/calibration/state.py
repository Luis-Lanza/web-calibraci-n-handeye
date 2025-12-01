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
        await self.check_auth()
        
        # Extract calibration_id from URL parameters
        # Reflex stores route parameters in self.router.page.params
        calibration_id_str = self.router.page.params.get("calibration_id", "")
        
        if calibration_id_str:
            try:
                self.current_calibration_id = int(calibration_id_str)
            except (ValueError, TypeError):
                print(f"Invalid calibration_id: {calibration_id_str}")
                return
        
        if not self.current_calibration_id:
            print("No calibration_id found in URL or state")
            return
            
        response = await APIClient.get(f"/calibrations/{self.current_calibration_id}", token=self.token)
        if response.status_code == 200:
            self.calibration = response.json()
        else:
            print(f"Failed to load calibration: {response.status_code} - {response.text}")
    
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
                # Update calibration with results
                self.calibration.update(result)
                self.calibration["status"] = "completed"
                await self.load_calibration()
                return rx.redirect(f"/calibration/{self.current_calibration_id}/results")
            else:
                return rx.window_alert(f"Error: {result.get('error_message')}")
        else:
            return rx.window_alert("Error de servidor al ejecutar calibración")

    @rx.var
    def matrix_formatted(self) -> str:
        """Format transformation matrix as readable text."""
        if not self.calibration or "transformation_matrix" not in self.calibration:
            return "No hay matriz disponible"
        
        matrix = self.calibration.get("transformation_matrix", [[0]*4]*4)
        try:
            lines = []
            for row in matrix:
                formatted_row = "  ".join(f"{val:10.6f}" for val in row)
                lines.append(formatted_row)
            return "\n".join(lines)
        except (TypeError, ValueError, KeyError):
            return str(matrix)
    
    @rx.var
    def rotation_error_formatted(self) -> str:
        """Format rotation error."""
        if not self.calibration:
            return "0.00"
        try:
            val = self.calibration.get("rotation_error_deg", 0)
            return f"{float(val):.2f}"
        except (TypeError, ValueError):
            return "0.00"
    
    @rx.var
    def translation_error_formatted(self) -> str:
        """Format translation error."""
        if not self.calibration:
            return "0.00"
        try:
            val = self.calibration.get("translation_error_mm", 0)
            return f"{float(val):.2f}"
        except (TypeError, ValueError):
            return "0.00"
    
    @rx.var
    def reprojection_error_formatted(self) -> str:
        """Format reprojection error."""
        if not self.calibration:
            return "0.00"
        try:
            val = self.calibration.get("reprojection_error", 0)
            return f"{float(val):.2f}"
        except (TypeError, ValueError):
            return "0.00"
    
    @rx.var
    def poses_summary(self) -> str:
        """Format poses processed summary."""
        if not self.calibration:
            return "0/0"
        try:
            valid = self.calibration.get("poses_valid", 0)
            total = self.calibration.get("poses_processed", 0)
            return f"{valid}/{total}"
        except (TypeError, ValueError):
            return "0/0"
    
    async def download_report(self):
        """Download the calibration report."""
        if not self.current_calibration_id:
            return
            
        try:
            content = await APIClient.download(f"/calibrations/{self.current_calibration_id}/report", token=self.token)
            return rx.download(
                data=content,
                filename=f"report_calibration_{self.current_calibration_id}.pdf",
            )
        except Exception as e:
            print(f"Download error: {e}")
            return rx.window_alert("Error al descargar el reporte.")
    
    async def download_json(self):
        """Download calibration results as JSON."""
        if not self.current_calibration_id:
            return
            
        try:
            content = await APIClient.download(f"/calibrations/{self.current_calibration_id}/export/json", token=self.token)
            return rx.download(
                data=content,
                filename=f"calibration_{self.current_calibration_id}.json",
            )
        except Exception as e:
            print(f"Download error: {e}")
            return rx.window_alert("Error al descargar JSON.")
    
    async def download_csv(self):
        """Download calibration matrix as CSV."""
        if not self.current_calibration_id:
            return
            
        try:
            content = await APIClient.download(f"/calibrations/{self.current_calibration_id}/export/csv", token=self.token)
            return rx.download(
                data=content,
                filename=f"calibration_{self.current_calibration_id}.csv",
            )
        except Exception as e:
            print(f"Download error: {e}")
            return rx.window_alert("Error al descargar CSV.")
    
    async def download_txt(self):
        """Download calibration summary as TXT."""
        if not self.current_calibration_id:
            return
            
        try:
            content = await APIClient.download(f"/calibrations/{self.current_calibration_id}/export/txt", token=self.token)
            return rx.download(
                data=content,
                filename=f"calibration_{self.current_calibration_id}.txt",
            )
        except Exception as e:
            print(f"Download error: {e}")
            return rx.window_alert("Error al descargar TXT.")
