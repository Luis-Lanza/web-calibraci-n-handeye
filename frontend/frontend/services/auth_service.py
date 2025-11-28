import reflex as rx
from .api_client import APIClient

class AuthService:
    """Service for authentication."""
    
    @staticmethod
    async def login(username: str, password: str, client_secret: str = None):
        data = {"username": username, "password": password}
        if client_secret:
            data["client_secret"] = client_secret
            
        response = await APIClient.post(
            "/token", 
            data=data
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 401:
             return {"success": False, "error": "Unauthorized", "status": 401, "detail": response.json().get("detail")}
        else:
            return {"success": False, "error": "Invalid credentials", "status": response.status_code}
            
    @staticmethod
    async def get_me(token: str):
        response = await APIClient.get("/users/me", token=token)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to fetch user"}
