"""Global styles and theme configuration."""
import reflex as rx

# Discreet Palette
class ColorPalette:
    """Discreet Palette"""
    PRIMARY = "#a275c2"      # Lavanda vibrante
    SECONDARY = "#8866a0"    # Lavanda más oscuro
    BACKGROUND = "#fdf7ff"   # Blanco lavanda
    ACCENT = "#d5cabd"       # Beige/Taupe
    GRAY_800 = "#1a202c"     # Gris muy oscuro para texto (mejor contraste)
    GRAY_700 = "#2d3748"     # Gris oscuro para texto
    GRAY_600 = "#4a5568"     # Gris medio para texto secundario
    GRAY_400 = "#718096"     # Gris medio para bordes/elementos visibles
    SUCCESS = "#48bb78"      # Verde para éxito
    ERROR = "#f56565"        # Rojo para error


STYLES = {
    "font_family": "Inter, system-ui, sans-serif",
    "background_color": ColorPalette.BACKGROUND,
    "color": ColorPalette.GRAY_800,  # Default text color - dark for readability
}

BUTTON_STYLE = {
    "background": ColorPalette.PRIMARY,
    "color": "white",
    "border_radius": "8px",
    "padding": "10px 20px",
    "cursor": "pointer",
    "_hover": {
        "background": ColorPalette.SECONDARY,
    }
}

INPUT_STYLE = {
    "border": f"1px solid {ColorPalette.ACCENT}",
    "border_radius": "6px",
    "padding": "8px 12px",
    "color": ColorPalette.GRAY_800,
    "_focus": {
        "border_color": ColorPalette.PRIMARY,
        "outline": "none",
    }
}

CARD_STYLE = {
    "background": "white",
    "border": f"1px solid {ColorPalette.ACCENT}",
    "border_radius": "12px",
    "padding": "20px",
    "box_shadow": "0 2px 8px rgba(162, 117, 194, 0.1)",
}

TEXT_SECONDARY = {
    "color": ColorPalette.GRAY_700,  # Darker for better contrast
}

TEXT_MUTED = {
    "color": ColorPalette.GRAY_600,  # Darker for better contrast
}

HEADING_STYLE = {
    "color": ColorPalette.GRAY_800,  # Dark headings by default
}
