import reflex as rx
from .state import CalibrationState
from ...components.layout import layout
from ...styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

def execute_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.heading("Paso 3: Ejecutar Calibración", size="6", color=ColorPalette.PRIMARY),
            
            rx.text("Verifica que los datos sean correctos antes de ejecutar.", color="gray"),
            
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.heading("Resumen de Datos", size="4"),
                        rx.hstack(
                            rx.text("Imágenes:", weight="bold"),
                            rx.text(f"{CalibrationState.images.length()}"),
                        ),
                        rx.hstack(
                            rx.text("Poses Robot:", weight="bold"),
                            rx.text(f"{CalibrationState.poses.length()}"),
                        ),
                        rx.divider(),
                        rx.cond(
                            CalibrationState.images.length() == CalibrationState.poses.length(),
                            rx.badge("Datos Sincronizados", color_scheme="green"),
                            rx.badge("Desajuste de Datos", color_scheme="red"),
                        ),
                        align_items="start",
                        spacing="2",
                    ),
                    style=CARD_STYLE,
                    width="100%",
                ),
                rx.box(
                    rx.vstack(
                        rx.heading("Configuración", size="4"),
                        rx.text(f"Método: Tsai-Lenz"),
                        rx.text(f"Tablero: {CalibrationState.calibration['charuco_squares_x']}x{CalibrationState.calibration['charuco_squares_y']}"),
                        align_items="start",
                        spacing="2",
                    ),
                    style=CARD_STYLE,
                    width="100%",
                ),
                columns="2",
                spacing="6",
                width="100%",
            ),
            
            rx.button(
                "EJECUTAR CALIBRACIÓN",
                on_click=CalibrationState.run_calibration,
                style=BUTTON_STYLE,
                size="4",
                width="100%",
                margin_top="6",
                is_disabled=rx.cond(
                    (CalibrationState.images.length() > 0) & 
                    (CalibrationState.images.length() == CalibrationState.poses.length()),
                    False, True
                ),
            ),
            
            spacing="6",
            width="100%",
            align_items="start",
        )
    )
