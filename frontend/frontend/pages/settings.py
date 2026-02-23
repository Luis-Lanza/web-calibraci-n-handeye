import reflex as rx
from ..state import AuthState
from ..components.layout import layout
from ..services.api_client import APIClient
from ..styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

class SettingsState(AuthState):
    """State for settings page."""
    show_mfa_dialog: bool = False
    verification_code: str = ""
    mfa_enabled: bool = False
    
    async def load_settings(self):
        """Load current settings."""
        if auth_error := await self.check_auth():
            return auth_error
            
        print("Loading MFA status...")
        response = await APIClient.get("/mfa/status", token=self.token)
        if response.status_code == 200:
            self.mfa_enabled = response.json().get("mfa_enabled", False)
        else:
            print(f"Error loading MFA status: {response.text}")
            
    async def toggle_mfa(self, enabled: bool):
        """Enable or disable MFA."""
        if enabled:
            # Step 1: Request code generation
            response = await APIClient.post("/mfa/generate", token=self.token)
            if response.status_code == 200:
                self.show_mfa_dialog = True
            else:
                return rx.window_alert("Error al generar código de verificación.")
        else:
            # Disable immediately
            response = await APIClient.post("/mfa/disable", token=self.token)
            if response.status_code == 200:
                self.mfa_enabled = False
                return rx.window_alert("Autenticación de dos factores desactivada.")
            else:
                return rx.window_alert("Error al desactivar MFA.")

    def set_verification_code(self, value: str):
        self.verification_code = value

    async def confirm_mfa_enable(self):
        """Step 2: Verify code and enable MFA."""
        if not self.verification_code:
            return rx.window_alert("Por favor ingrese el código.")
            
        data = {"code": self.verification_code}
        response = await APIClient.post("/mfa/enable", json_data=data, token=self.token)
        
        if response.status_code == 200:
            self.mfa_enabled = True
            self.show_mfa_dialog = False
            self.verification_code = ""
            return rx.window_alert("MFA activado exitosamente.")
        else:
            detail = response.json().get("detail", "Código inválido")
            return rx.window_alert(f"Error: {detail}")

    def cancel_mfa_enable(self):
        """Cancel MFA enablement."""
        self.show_mfa_dialog = False
        self.verification_code = ""
        # Switch will visually reverb because mfa_enabled is still False

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
            
            # MFA Verification Dialog
            rx.dialog.root(
                rx.dialog.content(
                    rx.dialog.title("Verificar Configuración MFA"),
                    rx.dialog.description(
                        "Se ha enviado un código de verificación a tu correo electrónico. Ingrésalo para confirmar."
                    ),
                    rx.vstack(
                        rx.input(
                            placeholder="Código (ej. 123456)",
                            value=SettingsState.verification_code,
                            on_change=SettingsState.set_verification_code,
                        ),
                        rx.flex(
                            rx.dialog.close(
                                rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=SettingsState.cancel_mfa_enable)
                            ),
                            rx.button("Verificar y Activar", on_click=SettingsState.confirm_mfa_enable),
                            spacing="3",
                            justify="end",
                            width="100%"
                        ),
                        spacing="4",
                        margin_top="4",
                    ),
                ),
                open=SettingsState.show_mfa_dialog,
                on_open_change=SettingsState.cancel_mfa_enable, # Close on click outside
            ),
            
            width="100%",
            align_items="start",
            on_mount=SettingsState.load_settings,
        )
    )
