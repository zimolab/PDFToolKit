import os
import webbrowser

from pyguiadapter.action import Action
from pyguiadapter.utils.messagebox import show_text_file, show_about_message
from pyguiadapter.window import BaseWindow

from ..constants import CURRENT_DIR, APP_AUTHOR, LICENSE, REPOSITORY

LICENSE_FILE = os.path.join(CURRENT_DIR, "assets/LICENSE.txt")
ABOUT_MESSAGE = (
    "PDFToolkit is an free and open-source software for PDF manipulation. "
    f"It is developed by {APP_AUTHOR} and is distributed under the {LICENSE} license.\n\n"
    f"This software is built with Python, PyGUIAdapter, PyMuPDF, and many other open-source projects."
)


# noinspection PyUnusedLocal
def on_action_license(window: BaseWindow, action: Action):
    """Show the license file"""
    show_text_file(
        window,
        LICENSE_FILE,
        text_format="plaintext",
        title="License",
        icon="fa.file-text",
    )


# noinspection PyUnusedLocal
def on_action_about(window: BaseWindow, action: Action):
    """Show the about message box"""
    show_about_message(window, ABOUT_MESSAGE, title="About PDFToolkit")


# noinspection PyUnusedLocal
def on_action_homepage(window: BaseWindow, action: Action):
    webbrowser.open_new_tab(REPOSITORY)


ACTION_LICENSE = Action(
    text="License", icon="fa.file-text", on_triggered=on_action_license
)
ACTION_ABOUT = Action(text="About", icon="fa.info-circle", on_triggered=on_action_about)
ACTION_HOMEPAGE = Action(
    text="Homepage", icon="fa.home", on_triggered=on_action_homepage
)
