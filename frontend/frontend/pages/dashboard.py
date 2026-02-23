import reflex as rx
from ..state import AuthState
from ..services.api_client import APIClient
from ..components.layout import layout
from ..styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

class DashboardState(AuthState):
    """State for the dashboard page."""
    calibrations: list[dict] = []
    show_confirm_delete: bool = False
    calibration_to_delete_id: int = 0
    
    async def load_calibrations(self):
        """Load calibrations from API."""
        if auth_error := await self.check_auth():
            return auth_error
            
        response = await APIClient.get("/calibrations", token=self.token)
        if response.status_code == 200:
            self.calibrations = response.json()
        else:
            print(f"Error loading calibrations: {response.text}")

    def create_calibration(self):
        return rx.redirect("/calibration/new")
        
    def view_calibration(self, cal: dict):
        """Smart redirect based on calibration status."""
        status = cal.get("status", "pending")
        cal_id = cal.get("id")
        
        if status in ["completed", "failed"]:
            return rx.redirect(f"/calibration/{cal_id}/results")
        else:
            return rx.redirect(f"/calibration/{cal_id}/images")

    def ask_delete_calibration(self, cal_id: int):
        """Open confirmation dialog for deletion."""
        self.calibration_to_delete_id = cal_id
        self.show_confirm_delete = True

    def cancel_delete(self):
        """Close confirmation dialog."""
        self.show_confirm_delete = False
        self.calibration_to_delete_id = 0

    async def confirm_delete_calibration(self):
        """Execute deletion."""
        if self.calibration_to_delete_id:
            response = await APIClient.delete(f"/calibrations/{self.calibration_to_delete_id}", token=self.token)
            if response.status_code == 204:
                # Remove from list locally
                self.calibrations = [c for c in self.calibrations if c["id"] != self.calibration_to_delete_id]
                # Or reload from server: await self.load_calibrations()
            else:
                print(f"Error deleting: {response.text}")
                return rx.window_alert("Error al eliminar la calibración")
                
        self.show_confirm_delete = False
        self.calibration_to_delete_id = 0

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
                rx.cond(
                    DashboardState.can_create_calibration,
                    rx.button(
                        "Borrar",
                        size="2",
                        variant="ghost",
                        color_scheme="red",
                        on_click=lambda: DashboardState.ask_delete_calibration(cal["id"]),
                    ),
                ),
                rx.button(
                    "Ver Detalles",
                    size="2",
                    variant="outline",
                    color_scheme="purple",
                    on_click=lambda: DashboardState.view_calibration(cal),
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
                rx.cond(
                    DashboardState.can_create_calibration,
                    rx.button(
                        "+ Nueva Calibración",
                        style=BUTTON_STYLE,
                        on_click=DashboardState.create_calibration,
                    ),
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
                        rx.cond(
                            DashboardState.can_create_calibration,
                            rx.button(
                                "Crear la primera",
                                variant="ghost",
                                on_click=DashboardState.create_calibration,
                            ),
                        ),
                    ),
                    padding="10",
                    width="100%",
                ),
            ),
            
            # Confirmation Dialog
            rx.alert_dialog.root(
                rx.alert_dialog.content(
                    rx.alert_dialog.title("Confirmar Eliminación"),
                    rx.alert_dialog.description(
                        "¿Estás seguro de que quieres eliminar esta calibración? Esta acción no se puede deshacer."
                    ),
                    rx.flex(
                        rx.alert_dialog.cancel(
                            rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=DashboardState.cancel_delete)
                        ),
                        rx.alert_dialog.action(
                            rx.button("Eliminar", color_scheme="red", on_click=DashboardState.confirm_delete_calibration)
                        ),
                        spacing="3",
                        margin_top="4",
                        justify="end",
                    ),
                ),
                open=DashboardState.show_confirm_delete,
            ),
            
            width="100%",
            align_items="start",
        )
    )
