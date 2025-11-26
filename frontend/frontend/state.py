import reflex as rx
from typing import Optional, Dict
from .services.auth_service import AuthService

class AuthState(rx.State):
    """The authentication state for the app."""
    token: str = rx.LocalStorage()
    user: Optional[Dict] = None
    is_authenticated: bool = False
    
    async def check_auth(self):
        """Check if the user is authenticated."""
        if self.token:
            result = await AuthService.get_me(self.token)
            if result["success"]:
                self.user = result["data"]
                self.is_authenticated = True
            else:
                self.logout()
        else:
            self.is_authenticated = False

    def logout(self):
        """Log out the user."""
        self.token = ""
        self.user = None
        self.is_authenticated = False
        return rx.redirect("/login")

    async def login(self, form_data: dict):
        """Log in the user."""
        username = form_data.get("username")
        password = form_data.get("password")
        
        result = await AuthService.login(username, password)
        
        if result["success"]:
            self.token = result["data"]["access_token"]
            self.is_authenticated = True
            return rx.redirect("/")
        else:
            return rx.window_alert("Credenciales inválidas")
