import reflex as rx
from ..state import AuthState
from ..services.api_client import APIClient
from ..components.layout import layout
from ..styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

class DashboardState(AuthState):
    """State for the dashboard page."""
    calibrations: list[dict] = []
    
    async def load_calibrations(self):
        """Load calibrations from API."""
        response = await APIClient.get("/calibrations", token=self.token)
        if response.status_code == 200:
            self.calibrations = response.json()
        else:
            print(f"Error loading calibrations: {response.text}")

    def create_calibration(self):
        return rx.redirect("/calibration/new")
        
    def view_calibration(self, cal_id: int):
        return rx.redirect(f"/calibration/{cal_id}")

def status_badge(status: str) -> rx.Component:
    colors = {
        "pending": "gray",
        "processing": "blue",
        "completed": "green",
        "failed": "red",
    }
    return rx.badge(status, color_scheme=colors.get(status, "gray"))

def calibration_card(cal: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.heading(cal["name"], size="4", color=ColorPalette.PRIMARY),
                rx.spacer(),
                status_badge(cal["status"]),
                width="100%",
            ),
            rx.text(cal["description"], color=ColorPalette.GRAY_600, size="2"),
            rx.divider(margin_y="2"),
            rx.hstack(
                rx.text(f"ID: {cal['id']}", size="1", color=ColorPalette.GRAY_600),
                rx.spacer(),
                rx.button(
                    "Ver Detalles",
                    size="2",
                    variant="outline",
                    color_scheme="purple",
                    on_click=lambda: DashboardState.view_calibration(cal["id"]),
                ),
                width="100%",
                align_items="center",
            ),
            align_items="start",
            spacing="2",
        ),
        style=CARD_STYLE,
        width="100%",
    )

def dashboard_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.heading("Mis Calibraciones", size="6", color=ColorPalette.GRAY_800),
                rx.spacer(),
                rx.button(
                    "+ Nueva Calibración",
                    style=BUTTON_STYLE,
                    on_click=DashboardState.create_calibration,
                ),
                width="100%",
                margin_bottom="6",
                align_items="center",
            ),
            
            rx.cond(
                DashboardState.calibrations,
                rx.grid(
                    rx.foreach(
                        DashboardState.calibrations,
                        calibration_card
                    ),
                    columns="3",
                    spacing="4",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.text("No hay calibraciones aún.", color="gray"),
                        rx.button(
                            "Crear la primera",
                            variant="ghost",
                            on_click=DashboardState.create_calibration,
                        ),
                    ),
                    padding="10",
                    width="100%",
                ),
            ),
            width="100%",
            align_items="start",
        )
    )
