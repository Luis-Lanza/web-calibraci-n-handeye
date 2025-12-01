import reflex as rx
from .state import CalibrationState
from ...components.layout import layout
from ...styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

def results_page() -> rx.Component:
    return layout(
        rx.vstack(
            rx.hstack(
                rx.heading("Resultados de Calibración", size="6", color=ColorPalette.PRIMARY),
                rx.spacer(),
                rx.menu.root(
                    rx.menu.trigger(
                        rx.button(
                            "Exportar Resultados",
                            variant="solid",
                            color_scheme="blue",
                        ),
                    ),
                    rx.menu.content(
                        rx.menu.item(
                            "Reporte PDF",
                            on_click=CalibrationState.download_report,
                        ),
                        rx.menu.separator(),
                        rx.menu.item(
                            "JSON (Completo)",
                            on_click=CalibrationState.download_json,
                        ),
                        rx.menu.item(
                            "CSV (Matriz)",
                            on_click=CalibrationState.download_csv,
                        ),
                        rx.menu.item(
                            "TXT (Legible)",
                            on_click=CalibrationState.download_txt,
                        ),
                    ),
                ),
                rx.button(
                    "Volver al Dashboard",
                    on_click=rx.redirect("/"),
                    variant="outline",
                ),
                width="100%",
                align_items="center",
            ),
            
            rx.cond(
                CalibrationState.calibration["status"] == "completed",
                rx.vstack(
                    # Success badge
                    rx.callout(
                        "Calibración completada exitosamente",
                        icon="check",
                        color_scheme="green",
                        variant="soft",
                        size="2",
                        style={"color": "#1b5e20", "background_color": "#e8f5e9", "border": "1px solid #c8e6c9"},
                    ),
                    
                    # Transformation Matrix
                    rx.box(
                        rx.vstack(
                            rx.heading("Matriz de Transformación Hand-Eye (4×4)", size="4", margin_bottom="2", color=ColorPalette.GRAY_800),
                            rx.text(
                                CalibrationState.calibration["method"],
                                size="2",
                                color=ColorPalette.GRAY_600,
                                margin_bottom="4",
                            ),
                            
                            # Matrix formatted nicely
                            rx.box(
                                CalibrationState.matrix_formatted,
                                style={
                                    "white_space": "pre",
                                    "font_family": "monospace",
                                    "font_size": "15px",
                                    "font_weight": "500",
                                    "background": "#ffffff",
                                    "padding": "24px",
                                    "border_radius": "8px",
                                    "border": f"2px solid {ColorPalette.PRIMARY}",
                                    "line_height": "2.0",
                                    "color": ColorPalette.GRAY_800,
                                },
                            ),
                            
                            align_items="start",
                        ),
                        style=CARD_STYLE,
                        width="100%",
                    ),
                    
                    # Metrics Grid
                    rx.grid(
                        # Reprojection Error
                        rx.box(
                            rx.vstack(
                                rx.text("Error de Reproyección", size="2", weight="bold", color=ColorPalette.GRAY_700),
                                rx.heading(
                                    CalibrationState.reprojection_error_formatted,
                                    size="7",
                                    color=ColorPalette.PRIMARY
                                ),
                                rx.text("mm", size="2", color=ColorPalette.GRAY_600),
                                align_items="center",
                                spacing="1",
                            ),
                            style=CARD_STYLE,
                        ),
                        
                        # Rotation Error
                        rx.box(
                            rx.vstack(
                                rx.text("Error de Rotación", size="2", weight="bold", color=ColorPalette.GRAY_700),
                                rx.heading(
                                    CalibrationState.rotation_error_formatted,
                                    size="7",
                                    color=ColorPalette.SECONDARY
                                ),
                                rx.text("grados", size="2", color=ColorPalette.GRAY_600),
                                align_items="center",
                                spacing="1",
                            ),
                            style=CARD_STYLE,
                        ),
                        
                        # Translation Error
                        rx.box(
                            rx.vstack(
                                rx.text("Error de Traslación", size="2", weight="bold", color=ColorPalette.GRAY_700),
                                rx.heading(
                                    CalibrationState.translation_error_formatted,
                                    size="7",
                                    color=ColorPalette.ACCENT
                                ),
                                rx.text("mm", size="2", color=ColorPalette.GRAY_600),
                                align_items="center",
                                spacing="1",
                            ),
                            style=CARD_STYLE,
                        ),
                        
                        # Poses Processed
                        rx.box(
                            rx.vstack(
                                rx.text("Poses Procesadas", size="2", weight="bold", color=ColorPalette.GRAY_700),
                                rx.heading(
                                    CalibrationState.poses_summary,
                                    size="7",
                                    color=ColorPalette.PRIMARY
                                ),
                                rx.text("válidas", size="2", color=ColorPalette.GRAY_600),
                                align_items="center",
                                spacing="1",
                            ),
                            style=CARD_STYLE,
                        ),
                        
                        columns="4",
                        spacing="4",
                        width="100%",
                    ),
                    
                    spacing="6",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.callout(
                            "Calibración fallida o pendiente",
                            icon="triangle-alert",
                            color_scheme="red",
                            size="2",
                        ),
                        rx.text("Revisa los logs o intenta nuevamente.", color=ColorPalette.GRAY_600),
                        spacing="3",
                    ),
                    padding="10",
                ),
            ),
            
            spacing="6",
            width="100%",
            align_items="start",
        )
    )
