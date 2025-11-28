import reflex as rx
from ..state import AuthState
from ..components.layout import layout
from ..services.api_client import APIClient
from ..styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

class SettingsState(AuthState):
    """State for settings page."""
    mfa_enabled: bool = False
    
    async def load_settings(self):
        """Load current settings."""
        response = await APIClient.get("/mfa/status", token=self.token)
        if response.status_code == 200:
            self.mfa_enabled = response.json().get("mfa_enabled", False)
            
    async def toggle_mfa(self, enabled: bool):
        """Enable or disable MFA."""
        endpoint = "/mfa/enable" if enabled else "/mfa/disable"
        response = await APIClient.post(endpoint, token=self.token)
        
        if response.status_code == 200:
            self.mfa_enabled = enabled
            action = "activada" if enabled else "desactivada"
            return rx.window_alert(f"Autenticación de dos factores {action} exitosamente.")
        else:
            return rx.window_alert("Error al actualizar la configuración.")

def settings_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading("Configuración de Cuenta", size="6", color=ColorPalette.GRAY_800),
            rx.divider(margin_y="4"),
            
            rx.box(
                rx.vstack(
                    rx.heading("Seguridad", size="4", color=ColorPalette.PRIMARY),
                    rx.text(
                        "Autenticación de Dos Factores (MFA)",
                        weight="bold",
                        color=ColorPalette.GRAY_800
                    ),
                    rx.text(
                        "Aumenta la seguridad de tu cuenta solicitando un código enviado a tu correo al iniciar sesión.",
                        color=ColorPalette.GRAY_600,
                        size="2"
                    ),
                    rx.hstack(
                        rx.text("Estado:", weight="medium"),
                        rx.cond(
                            SettingsState.mfa_enabled,
                            rx.badge("Activado", color_scheme="green"),
                            rx.badge("Desactivado", color_scheme="gray"),
                        ),
                        align_items="center",
                        spacing="2",
                    ),
                    rx.switch(
                        is_checked=SettingsState.mfa_enabled,
                        on_change=SettingsState.toggle_mfa,
                    ),
                    align_items="start",
                    spacing="3",
                ),
                style=CARD_STYLE,
                width="100%",
                max_width="600px",
            ),
            
            width="100%",
            align_items="start",
            on_mount=SettingsState.load_settings,
        )
    )
