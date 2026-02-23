import reflex as rx
from .state import CalibrationState
from ...components.layout import layout
from ...styles import ColorPalette, BUTTON_STYLE, INPUT_STYLE, CARD_STYLE

def poses_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.button(
                    "← Volver",
                    on_click=rx.redirect(f"/calibration/{CalibrationState.current_calibration_id}/images"),
                    variant="outline",
                    color=ColorPalette.PRIMARY,
                    border=f"1px solid {ColorPalette.PRIMARY}",
                    size="2",
                    _hover={"background": ColorPalette.PRIMARY, "color": "white"},
                ),
                rx.heading("Paso 2: Poses del Robot", size="6", color=ColorPalette.PRIMARY),
                rx.spacer(),
                rx.button(
                    "Siguiente: Ejecutar >",
                    on_click=rx.redirect(f"/calibration/{CalibrationState.current_calibration_id}/execute"),
                    style=BUTTON_STYLE,
                    is_disabled=rx.cond(CalibrationState.poses, False, True),
                ),
                width="100%",
                align_items="center",
            ),
            
            rx.text("Importa las poses del robot correspondientes a cada imagen.", color="gray"),
            
            rx.grid(
                # CSV Import Section
                rx.box(
                    rx.vstack(
                        rx.heading("Importar CSV", size="4"),
                        rx.text("Formato: X, Y, Z, Rx, Ry, Rz o X, Y, Z, A, B, C", size="2", color="gray"),
                        rx.upload(
                            rx.button("Seleccionar CSV", color=ColorPalette.PRIMARY, bg="white", border=f"1px solid {ColorPalette.PRIMARY}"),
                            id="upload_csv",
                            border=f"1px dashed {ColorPalette.ACCENT}",
                            padding="4",
                            border_radius="md",
                            accept={".csv": [".csv"]},
                            max_files=1,
                        ),
                        rx.button(
                            "Importar",
                            on_click=CalibrationState.upload_csv(rx.upload_files("upload_csv")),
                            style=BUTTON_STYLE,
                            width="100%",
                        ),
                        spacing="4",
                        align_items="stretch",
                    ),
                    style=CARD_STYLE,
                ),
                
                # Manual Entry Section (Placeholder for now)
                rx.box(
                    rx.vstack(
                        rx.heading("Entrada Manual", size="4"),
                        rx.text("Funcionalidad en desarrollo...", size="2", color="gray"),
                        spacing="4",
                    ),
                    style=CARD_STYLE,
                    opacity="0.5",
                ),
                columns="2",
                spacing="6",
                width="100%",
            ),
            
            rx.divider(),
            
            rx.heading(f"Poses Cargadas ({CalibrationState.poses.length()})", size="4"),
            
            rx.cond(
                CalibrationState.poses,
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("Index"),
                            rx.table.column_header_cell("X"),
                            rx.table.column_header_cell("Y"),
                            rx.table.column_header_cell("Z"),
                            rx.table.column_header_cell("Rx"),
                            rx.table.column_header_cell("Ry"),
                            rx.table.column_header_cell("Rz"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            CalibrationState.poses,
                            lambda pose: rx.table.row(
                                rx.table.cell(pose["pose_index"], color=ColorPalette.GRAY_800),
                                rx.table.cell(pose["x"], color=ColorPalette.GRAY_800),
                                rx.table.cell(pose["y"], color=ColorPalette.GRAY_800),
                                rx.table.cell(pose["z"], color=ColorPalette.GRAY_800),
                                rx.table.cell(pose["rx"], color=ColorPalette.GRAY_800),
                                rx.table.cell(pose["ry"], color=ColorPalette.GRAY_800),
                                rx.table.cell(pose["rz"], color=ColorPalette.GRAY_800),
                            )
                        )
                    ),
                    width="100%",
                ),
                rx.text("No hay poses cargadas aún.", color="gray", font_style="italic"),
            ),
            
            spacing="6",
            width="100%",
            align_items="start",
        )
    )
