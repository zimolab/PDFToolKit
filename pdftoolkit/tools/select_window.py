"""
The main window of the PDF Toolkit application is defined in this module.

@author: zimolab
@created: 2024-12-11
"""

import webbrowser
from typing import List, cast

import i18n
import qdarktheme
from pyguiadapter.action import Action
from pyguiadapter.action import Separator
from pyguiadapter.menu import Menu
from pyguiadapter.utils import show_info_message
from pyguiadapter.utils.messagebox import (
    show_text_content,
    show_about_message,
    show_critical_message,
)
from pyguiadapter.window import BaseWindow
from pyguiadapter.window import SimpleWindowEventListener
from pyguiadapter.windows.fnselect import FnSelectWindowConfig, FnSelectWindow

from .commons.winconf import DEFAULT_WINDOW_SIZE, DEFAULT_DOCUMENT_DOCK_WIDTH
from ..assets import license_file, locales_file
from ..configuration import (
    GlobalConfig,
    DEFAULT_LANGUAGE,
    get_theme_safely,
    get_language_map,
)
from ..metadata import APP_NAME
from ..metadata import AUTHOR, LICENSE, REPOSITORY, VERSION
from ..translation import t, select_win_t, app_t
from ..utils import unused, read_asset_text_file

WINDOW_CONFIG = FnSelectWindowConfig(
    title=APP_NAME,
    icon="fa5s.file-pdf",
    size=DEFAULT_WINDOW_SIZE,
    document_browser_width=DEFAULT_DOCUMENT_DOCK_WIDTH,
)


# noinspection PyUnusedLocal
def on_window_create(window: FnSelectWindow):
    pass


# noinspection PyUnusedLocal
def on_window_close(window: FnSelectWindow) -> bool:
    return True


# noinspection PyUnusedLocal
def on_window_show(window: FnSelectWindow):
    pass


# noinspection PyUnusedLocal
def on_window_hide(window: FnSelectWindow):
    pass


WINDOW_LISTENER = SimpleWindowEventListener(
    on_create=on_window_create,
    on_close=on_window_close,
    on_show=on_window_show,
    on_hide=on_window_hide,
)


def _menu_t(key: str, prefix: str = "app.select_window.menu", **kwargs):
    return select_win_t(key, prefix=prefix, **kwargs)


# noinspection PyUnusedLocal
def on_action_license(window: BaseWindow, action: Action):
    license_content = read_asset_text_file(license_file())
    show_text_content(
        window,
        text_content=license_content,
        text_format="plaintext",
        title=select_win_t("license_dlg_title") + " - " + LICENSE,
        icon="fa.file-text",
    )


# noinspection PyUnusedLocal
def on_action_about(window: BaseWindow, action: Action):
    about_message = read_asset_text_file(
        locales_file(select_win_t("about_msg_file"))
    ).format(
        app_name=t("app.app_name"),
        author=AUTHOR,
        version=VERSION,
        license=LICENSE,
        repo=REPOSITORY,
    )
    show_about_message(
        window, title=select_win_t("about_dlg_title"), message=about_message
    )


# noinspection PyUnusedLocal
def on_action_homepage(window: BaseWindow, action: Action):
    webbrowser.open_new_tab(REPOSITORY)


def on_action_change_language(window: BaseWindow, action: Action):
    lang_code = action.data or DEFAULT_LANGUAGE
    if not lang_code:
        show_critical_message(
            window,
            title=app_t(f"error_dlg_title"),
            message=select_win_t("unknown_lang_msg").format(lang=action.text),
        )
        return
    i18n.set("locale", lang_code)
    GlobalConfig.language = lang_code
    GlobalConfig.save()
    show_info_message(
        window,
        title=app_t("success_dlg_title"),
        message=select_win_t("lang_changed_msg"),
    )


def on_action_change_theme(window: BaseWindow, action: Action):
    unused(window)
    theme, _ = get_theme_safely(cast(str, action.data))
    qdarktheme.setup_theme(theme)
    GlobalConfig.theme = theme
    GlobalConfig.save()


def _create_language_actions() -> List[Action]:
    lang_map = get_language_map(GlobalConfig.language_map)
    cur_lang = GlobalConfig.language or DEFAULT_LANGUAGE
    actions = []
    for lang_code, lang_name in lang_map.items():
        action = Action(
            text=lang_name,
            on_triggered=on_action_change_language,
            checkable=True,
            checked=(lang_code == cur_lang),
            data=lang_code,
        )
        actions.append(action)
    return actions


ACTION_LICENSE = Action(
    text=_menu_t("action_license"),
    icon="fa.file-text",
    on_triggered=on_action_license,
)
ACTION_ABOUT = Action(
    text=_menu_t("action_about"),
    icon="fa.info-circle",
    on_triggered=on_action_about,
)
ACTION_HOMEPAGE = Action(
    text=_menu_t("action_homepage"),
    icon="fa.home",
    on_triggered=on_action_homepage,
)

LANGUAGE_ACTIONS = _create_language_actions()


_current_theme, _ = get_theme_safely(GlobalConfig.theme)

ACTION_THEME_AUTO = Action(
    text=_menu_t(f"action_theme_auto"),
    checkable=True,
    checked=(_current_theme == "auto"),
    on_triggered=on_action_change_theme,
    data="auto",
)
ACTION_THEME_LIGHT = Action(
    text=_menu_t("action_theme_light"),
    checkable=True,
    checked=(_current_theme == "light"),
    on_triggered=on_action_change_theme,
    data="light",
)
ACTION_THEME_DARK = Action(
    text=_menu_t("action_theme_dark"),
    checkable=True,
    checked=(_current_theme == "dark"),
    on_triggered=on_action_change_theme,
    data="dark",
)

MENU_HELP = Menu(
    title=_menu_t("menu_help"),
    actions=[ACTION_ABOUT, Separator(), ACTION_HOMEPAGE, ACTION_LICENSE],
)

MENU_LANGUAGE = Menu(
    title=_menu_t("menu_language"),
    actions=LANGUAGE_ACTIONS,
    exclusive=True,
)

MENU_THEME = Menu(
    title=_menu_t("menu_theme"),
    actions=[
        ACTION_THEME_AUTO,
        ACTION_THEME_LIGHT,
        ACTION_THEME_DARK,
    ],
    exclusive=True,
)


WINDOW_MENUS = (MENU_LANGUAGE, MENU_THEME, MENU_HELP)
