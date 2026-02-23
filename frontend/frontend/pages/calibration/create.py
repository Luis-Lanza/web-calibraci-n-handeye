import reflex as rx
from .state import CalibrationState
from ...components.layout import layout
from ...styles import ColorPalette, BUTTON_STYLE, INPUT_STYLE, CARD_STYLE

def create_calibration_page() -> rx.Component:
    return layout(
        rx.center(
            rx.vstack(
                rx.hstack(
                    rx.button(
                        "← Volver",
                        on_click=rx.redirect("/"),
                        variant="outline",
                        color=ColorPalette.PRIMARY,
                        border=f"1px solid {ColorPalette.PRIMARY}",
                        size="2",
                        _hover={"background": ColorPalette.PRIMARY, "color": "white"},
                    ),
                    rx.heading("Nueva Calibración", size="6", color=ColorPalette.PRIMARY),
                    width="100%",
                    align_items="center",
                    spacing="3",
                ),
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
                        
                        rx.divider(),
                        
                        # Camera Parameters Section (Required)
                        rx.heading("Parámetros de Cámara", size="4"),
                        rx.text(
                            "Parámetros intrínsecos de calibración de la cámara",
                            color="gray",
                            size="2"
                        ),
                        
                        rx.heading("Matriz Intrínseca", size="3", margin_top="3"),
                        rx.grid(
                            rx.vstack(
                                rx.text("fx (Focal X)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_fx.to_string(),
                                    on_change=CalibrationState.set_camera_fx,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("fy (Focal Y)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_fy.to_string(),
                                    on_change=CalibrationState.set_camera_fy,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("cx (Centro X)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_cx.to_string(),
                                    on_change=CalibrationState.set_camera_cx,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("cy (Centro Y)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_cy.to_string(),
                                    on_change=CalibrationState.set_camera_cy,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            columns="2",
                            spacing="3",
                            width="100%"
                        ),
                        
                        rx.heading("Coeficientes de Distorsión", size="3", margin_top="3"),
                        rx.grid(
                            rx.vstack(
                                rx.text("k1 (Radial)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_k1.to_string(),
                                    on_change=CalibrationState.set_camera_k1,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("k2 (Radial)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_k2.to_string(),
                                    on_change=CalibrationState.set_camera_k2,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("p1 (Tangencial)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_p1.to_string(),
                                    on_change=CalibrationState.set_camera_p1,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("p2 (Tangencial)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_p2.to_string(),
                                    on_change=CalibrationState.set_camera_p2,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            rx.vstack(
                                rx.text("k3 (Radial)", size="2", weight="bold"),
                                rx.input(
                                    value=CalibrationState.camera_k3.to_string(),
                                    on_change=CalibrationState.set_camera_k3,
                                    type="number",
                                    style=INPUT_STYLE
                                )
                            ),
                            columns="2",
                            spacing="3",
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
