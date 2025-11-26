import reflex as rx
from ..state import AuthState
from ..styles import ColorPalette

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.heading("Hand-Eye Calibration", size="5", color="white"),
            rx.spacer(),
            rx.hstack(
                rx.text(AuthState.user["username"], color="white"),
                rx.button(
                    "Salir",
                    on_click=AuthState.logout,
                    variant="outline",
                    color_scheme="gray",
                    size="2",
                ),
                spacing="4",
                align_items="center",
            ),
            padding="4",
            background_color=ColorPalette.PRIMARY,
            align_items="center",
        ),
        width="100%",
    )

def layout(content: rx.Component) -> rx.Component:
    """Main layout for authenticated pages."""
    return rx.box(
        navbar(),
        rx.box(
            content,
            padding="6",
            max_width="1200px",
            margin="0 auto",
        ),
        background_color=ColorPalette.BACKGROUND,
        min_height="100vh",
    )
