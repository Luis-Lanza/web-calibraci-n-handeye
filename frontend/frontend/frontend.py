"""Welcome to Reflex! This file outlines the steps to create a basic app."""

import reflex as rx
from rxconfig import config
from .styles import STYLES
from .state import AuthState
from .pages.login import login_page
from .pages.dashboard import dashboard_page, DashboardState


from .pages.calibration.create import create_calibration_page
from .pages.calibration.images import images_page
from .pages.calibration.poses import poses_page
from .pages.calibration.execute import execute_page
from .pages.calibration.results import results_page
from .pages.calibration.state import CalibrationState

def index() -> rx.Component:
    return dashboard_page()

app = rx.App(style=STYLES)
app.add_page(login_page, route="/login")
app.add_page(index, route="/", on_load=DashboardState.load_calibrations)
app.add_page(create_calibration_page, route="/calibration/new")
app.add_page(images_page, route="/calibration/[calibration_id]/images", on_load=CalibrationState.load_calibration)
app.add_page(poses_page, route="/calibration/[calibration_id]/poses", on_load=CalibrationState.load_calibration)
app.add_page(execute_page, route="/calibration/[calibration_id]/execute", on_load=CalibrationState.load_calibration)
app.add_page(results_page, route="/calibration/[calibration_id]/results", on_load=CalibrationState.load_calibration)
