import reflex as rx
from ..state import AuthState
from ..styles import ColorPalette, BUTTON_STYLE, INPUT_STYLE, CARD_STYLE

def login_page() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.heading(
                "Hand-Eye Calibration", 
                size="8", 
                color=ColorPalette.PRIMARY,
                margin_bottom="4"
            ),
            rx.box(
                rx.form(
                    rx.vstack(
                        rx.heading("Iniciar Sesión", size="5", color=ColorPalette.GRAY_800),
                        rx.text("Ingresa tus credenciales para continuar", color=ColorPalette.SECONDARY, size="2"),
                        
                        rx.input(
                            placeholder="Usuario",
                            name="username",
                            style=INPUT_STYLE,
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            name="password",
                            type="password",
                            style=INPUT_STYLE,
                            width="100%",
                        ),
                        rx.cond(
                            AuthState.mfa_required,
                            rx.vstack(
                                rx.text("Código de Verificación (Email)", size="2", color=ColorPalette.PRIMARY, weight="bold"),
                                rx.input(
                                    placeholder="Código de 6 dígitos",
                                    name="mfa_code",
                                    style=INPUT_STYLE,
                                    width="100%",
                                ),
                                spacing="2",
                                width="100%",
                            ),
                        ),
                        rx.button(
                            "Entrar",
                            type="submit",
                            style=BUTTON_STYLE,
                            width="100%",
                            margin_top="4",
                        ),
                        spacing="4",
                        align_items="stretch",
                    ),
                    on_submit=AuthState.login,
                ),
                style=CARD_STYLE,
                width="400px",
            ),
            spacing="6",
            align_items="center",
        ),
        height="100vh",
        background_color=ColorPalette.BACKGROUND,
    )
