import reflex as rx
from .state import CalibrationState
from ...components.layout import layout
from ...styles import ColorPalette, BUTTON_STYLE, INPUT_STYLE, CARD_STYLE

def create_calibration_page() -> rx.Component:
    return layout(
        rx.center(
            rx.vstack(
                rx.heading("Nueva Calibración", size="6", color=ColorPalette.PRIMARY),
                rx.text("Configura los parámetros del tablero ChArUco", color="gray"),
                
                rx.box(
                    rx.vstack(
                        rx.text("Nombre", weight="bold"),
                        rx.input(
                            placeholder="Ej: Calibración Robot 1",
                            on_change=CalibrationState.set_new_cal_name,
                            style=INPUT_STYLE,
                            width="100%"
                        ),
                        
                        rx.text("Descripción", weight="bold"),
                        rx.text_area(
                            placeholder="Detalles opcionales...",
                            on_change=CalibrationState.set_new_cal_desc,
                            style=INPUT_STYLE,
                            width="100%"
                        ),
                        
                        rx.divider(),
                        rx.heading("Parámetros ChArUco", size="4"),
                        
                        rx.grid(
                            rx.vstack(
                                rx.text("Cuadros X"),
                                rx.input(
                                    value=CalibrationState.squares_x.to_string(),
                                    on_change=CalibrationState.set_squares_x,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("Cuadros Y"),
                                rx.input(
                                    value=CalibrationState.squares_y.to_string(),
                                    on_change=CalibrationState.set_squares_y,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            columns="2",
                            spacing="4",
                            width="100%"
                        ),
                        
                        rx.grid(
                            rx.vstack(
                                rx.text("Largo Cuadro (mm)"),
                                rx.input(
                                    value=CalibrationState.square_len.to_string(),
                                    on_change=CalibrationState.set_square_len,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("Largo Marcador (mm)"),
                                rx.input(
                                    value=CalibrationState.marker_len.to_string(),
                                    on_change=CalibrationState.set_marker_len,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            columns="2",
                            spacing="4",
                            width="100%"
                        ),
                        
                        rx.button(
                            "Crear Calibración",
                            on_click=CalibrationState.create_calibration,
                            style=BUTTON_STYLE,
                            width="100%",
                            margin_top="4"
                        ),
                        spacing="4",
                        align_items="stretch",
                    ),
                    style=CARD_STYLE,
                    width="600px",
                ),
                spacing="6",
            ),
            padding_top="10",
        )
    )
