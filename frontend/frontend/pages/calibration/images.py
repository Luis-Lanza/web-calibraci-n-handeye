import reflex as rx
from .state import CalibrationState
from ...components.layout import layout
from ...styles import ColorPalette, BUTTON_STYLE, CARD_STYLE

def images_page() -> rx.Component:
    return layout(
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
                rx.heading("Paso 1: Cargar Imágenes", size="6", color=ColorPalette.PRIMARY),
                rx.spacer(),
                rx.button(
                    "Siguiente: Poses del Robot >",
                    on_click=rx.redirect(f"/calibration/{CalibrationState.current_calibration_id}/poses"),
                    style=BUTTON_STYLE,
                    is_disabled=rx.cond(CalibrationState.images, False, True),
                ),
                width="100%",
                align_items="center",
            ),
            
            rx.text("Sube las imágenes del tablero ChArUco capturadas por la cámara.", color="gray"),
            
            rx.upload(
                rx.vstack(
                    rx.button("Seleccionar Imágenes", color=ColorPalette.PRIMARY, bg="white", border=f"1px solid {ColorPalette.PRIMARY}"),
                    rx.text("Arrastra y suelta archivos aquí", size="2", color="gray"),
                ),
                id="upload_images",
                border=f"1px dashed {ColorPalette.ACCENT}",
                padding="10",
                border_radius="lg",
                multiple=True,
                accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
                max_files=20,
            ),
            
            rx.hstack(
                rx.foreach(
                    rx.selected_files("upload_images"),
                    lambda file: rx.badge(file, color_scheme="purple")
                ),
                wrap="wrap",
                spacing="2",
            ),
            
            rx.button(
                "Subir Archivos Seleccionados",
                on_click=CalibrationState.upload_files(rx.upload_files("upload_images")),
                style=BUTTON_STYLE,
            ),
            
            rx.divider(),
            
            rx.heading(f"Imágenes Subidas ({CalibrationState.images.length()})", size="4", color=ColorPalette.GRAY_800),
            
            rx.cond(
                CalibrationState.images,
                rx.grid(
                    rx.foreach(
                        CalibrationState.images,
                        lambda img: rx.box(
                            rx.image(
                                # Use annotated image if available, otherwise original
                                src=rx.cond(
                                    img["annotated_image_path"],
                                    "http://localhost:8000/" + img["annotated_image_path"].to(str),
                                    "http://localhost:8000/" + img["image_path"].to(str)
                                ),
                                width="100%", 
                                height="auto", 
                                border_radius="md",
                                alt=img['original_filename']
                            ),
                            rx.hstack(
                                rx.text(img['original_filename'], size="1", color=ColorPalette.GRAY_600),
                                rx.cond(
                                    img["charuco_detected"],
                                    rx.badge("✓ " + img["corners_detected"].to(str) + " corners", color_scheme="green", size="1"),
                                    rx.badge("✗ No detectado", color_scheme="red", size="1"),
                                ),
                                spacing="2",
                                justify="between",
                                width="100%",
                                margin_top="2",
                            ),
                            style=CARD_STYLE,
                        )
                    ),
                    columns="4",
                    spacing="4",
                    width="100%",
                ),
                rx.text("No hay imágenes subidas aún.", color="gray", font_style="italic"),
            ),
            
            spacing="6",
            width="100%",
            align_items="start",
        )
    )
