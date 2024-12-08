import webbrowser
from pathlib import Path

from pyguiadapter.action import Action
from pyguiadapter.utils.messagebox import show_text_content, show_about_message
from pyguiadapter.window import BaseWindow
from pyguiadapter.action import Separator
from pyguiadapter.menu import Menu

from ..commons.app_meta import APP_AUTHOR, APP_LICENSE, APP_REPOSITORY, APP_VERSION
from ..commons.app_path import ASSETS_DIR
from ..commons.app_translation import t, LOCALES_DIR
from ..commons.utils import read_file


# locale prefix
_W = "app.select_window"
_M = f"{_W}.menu"


# noinspection PyUnusedLocal
def on_action_license(window: BaseWindow, action: Action):
    license_file = Path(ASSETS_DIR).joinpath("LICENSE.txt").absolute().as_posix()
    license_content = read_file(
        Path(ASSETS_DIR).joinpath("LICENSE.txt").absolute().as_posix()
    )
    show_text_content(
        window,
        text_content=license_content,
        text_format="plaintext",
        title=t(f"{_W}.license_dlg_title") + " - " + APP_LICENSE,
        icon="fa.file-text",
    )


# noinspection PyUnusedLocal
def on_action_about(window: BaseWindow, action: Action):
    about_message_file = Path(LOCALES_DIR).joinpath(t(f"{_W}.about_msg_file"))
    about_message = read_file(about_message_file.as_posix()).format(
        app_name=t("app.app_name"),
        author=APP_AUTHOR,
        version=APP_VERSION,
        license=APP_LICENSE,
        repo=APP_REPOSITORY,
    )
    show_about_message(window, title=t(f"{_W}.about_dlg_title"), message=about_message)


# noinspection PyUnusedLocal
def on_action_homepage(window: BaseWindow, action: Action):
    webbrowser.open_new_tab(APP_REPOSITORY)


ACTION_LICENSE = Action(
    text=t(f"{_M}.action_license"),
    icon="fa.file-text",
    on_triggered=on_action_license,
)
ACTION_ABOUT = Action(
    text=t(f"{_M}.action_about"),
    icon="fa.info-circle",
    on_triggered=on_action_about,
)
ACTION_HOMEPAGE = Action(
    text=t(f"{_M}.action_homepage"),
    icon="fa.home",
    on_triggered=on_action_homepage,
)


MENU_HELP = Menu(
    title=t(f"{_M}.menu_help"),
    actions=[ACTION_ABOUT, Separator(), ACTION_HOMEPAGE, ACTION_LICENSE],
)
