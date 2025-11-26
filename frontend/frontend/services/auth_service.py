import reflex as rx
from .api_client import APIClient

class AuthService:
    """Service for authentication."""
    
    @staticmethod
    async def login(username: str, password: str):
        response = await APIClient.post(
            "/token", 
            data={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Invalid credentials"}
            
    @staticmethod
    async def get_me(token: str):
        response = await APIClient.get("/users/me", token=token)
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        else:
            return {"success": False, "error": "Failed to fetch user"}
