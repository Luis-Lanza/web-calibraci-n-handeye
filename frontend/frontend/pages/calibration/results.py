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
                    rx.box(
                        rx.vstack(
                            rx.heading("Matriz de Transformación (Hand-Eye)", size="4"),
                            rx.code_block(
                                str(CalibrationState.calibration["transformation_matrix"]),
                                language="json",
                            ),
                        ),
                        style=CARD_STYLE,
                        width="100%",
                    ),
                    
                    rx.grid(
                        rx.box(
                            rx.vstack(
                                rx.heading("Error de Reproyección", size="3"),
                                rx.heading(f"{CalibrationState.calibration['reprojection_error']:.4f}", size="6", color=ColorPalette.PRIMARY),
                                rx.text("pixels", size="1"),
                            ),
                            style=CARD_STYLE,
                            align_items="center",
                        ),
                        columns="3",
                        spacing="4",
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                ),
                rx.center(
                    rx.vstack(
                        rx.heading("Calibración Fallida o Pendiente", size="5", color="red"),
                        rx.text("Revisa los logs o intenta nuevamente."),
                    ),
                    padding="10",
                ),
            ),
            
            spacing="6",
            width="100%",
            align_items="start",
        )
    )
