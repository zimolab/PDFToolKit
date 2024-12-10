import webbrowser
from pathlib import Path
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

from ..commons.app_config import (
    GlobalConfig,
    DEFAULT_LANGUAGE,
    get_theme_safely,
    get_language_map,
)
from ..commons.app_meta import APP_AUTHOR, APP_LICENSE, APP_REPOSITORY, APP_VERSION
from ..commons.app_path import ASSETS_DIR
from ..commons.app_translation import t, LOCALES_DIR
from ..commons.utils import read_file, unused

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


def on_action_change_language(window: BaseWindow, action: Action):
    lang_code = action.data or DEFAULT_LANGUAGE
    if not lang_code:
        show_critical_message(
            window,
            title=t(f"app.error_dlg_title"),
            message=t(f"{_W}.unknown_lang_msg").format(lang=action.text),
        )
        return
    i18n.set("locale", lang_code)
    GlobalConfig.language = lang_code
    GlobalConfig.save()
    show_info_message(
        window, title=t(f"app.success_dlg_title"), message=t(f"{_W}.lang_changed_msg")
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

LANGUAGE_ACTIONS = _create_language_actions()


_current_theme, _ = get_theme_safely(GlobalConfig.theme)

ACTION_THEME_AUTO = Action(
    text=t(f"{_M}.action_theme_auto"),
    checkable=True,
    checked=(_current_theme == "auto"),
    on_triggered=on_action_change_theme,
    data="auto",
)
ACTION_THEME_LIGHT = Action(
    text=t(f"{_M}.action_theme_light"),
    checkable=True,
    checked=(_current_theme == "light"),
    on_triggered=on_action_change_theme,
    data="light",
)
ACTION_THEME_DARK = Action(
    text=t(f"{_M}.action_theme_dark"),
    checkable=True,
    checked=(_current_theme == "dark"),
    on_triggered=on_action_change_theme,
    data="dark",
)

MENU_HELP = Menu(
    title=t(f"{_M}.menu_help"),
    actions=[ACTION_ABOUT, Separator(), ACTION_HOMEPAGE, ACTION_LICENSE],
)

MENU_LANGUAGE = Menu(
    title=t(f"{_M}.menu_language"),
    actions=LANGUAGE_ACTIONS,
    exclusive=True,
)

MENU_THEME = Menu(
    title=t(f"{_M}.menu_theme"),
    actions=[
        ACTION_THEME_AUTO,
        ACTION_THEME_LIGHT,
        ACTION_THEME_DARK,
    ],
    exclusive=True,
)
