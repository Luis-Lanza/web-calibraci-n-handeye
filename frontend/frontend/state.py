import reflex as rx
from typing import Optional, Dict
from .services.auth_service import AuthService

class AuthState(rx.State):
    """The authentication state for the app."""
    token: str = rx.LocalStorage()
    user: Optional[Dict] = None
    is_authenticated: bool = False
    mfa_required: bool = False
    
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
        self.mfa_required = False
        return rx.redirect("/login")

    async def login(self, form_data: dict):
        """Log in the user."""
        username = form_data.get("username")
        password = form_data.get("password")
        mfa_code = form_data.get("mfa_code", "")
        
        # If MFA is required, we pass the code as client_secret (hack for OAuth2 form)
        client_secret = mfa_code if self.mfa_required else None
        
        result = await AuthService.login(username, password, client_secret)
        
        if result["success"]:
            self.token = result["data"]["access_token"]
            self.is_authenticated = True
            self.mfa_required = False
            return rx.redirect("/")
        else:
            if result.get("status") == 401 and result.get("detail") == "MFA_REQUIRED":
                self.mfa_required = True
                return rx.window_alert("Código de verificación enviado a su correo.")
            
            if result.get("status") == 429:
                return rx.window_alert(result.get("detail"))
            
            return rx.window_alert("Credenciales inválidas o código incorrecto")

    @rx.var
    def is_technician(self) -> bool:
        """Check if user is a technician."""
        if not self.user:
            return False
        return self.user.get("role") == "technician"

    @rx.var
    def is_engineer(self) -> bool:
        """Check if user is an engineer."""
        if not self.user:
            return False
        return self.user.get("role") == "engineer"

    @rx.var
    def is_supervisor(self) -> bool:
        """Check if user is a supervisor."""
        if not self.user:
            return False
        return self.user.get("role") == "supervisor"

    @rx.var
    def can_create_calibration(self) -> bool:
        """Check if user can create calibrations."""
        return self.is_technician or self.is_engineer

    @rx.var
    def can_configure(self) -> bool:
        """Check if user can configure system."""
        return self.is_engineer
