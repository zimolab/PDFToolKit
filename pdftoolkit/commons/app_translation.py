from pathlib import Path

import i18n

from .app_config import DEFAULT_LANGUAGE, GlobalConfig
from .app_path import ASSETS_DIR

LOCALES_DIR = Path(ASSETS_DIR).joinpath("locales").absolute().as_posix()


def _init_i18n():
    i18n.load_path.append(LOCALES_DIR)
    i18n.set("fallback", DEFAULT_LANGUAGE)
    i18n.set("filename_format", "{namespace}.{locale}.{format}")
    i18n.set("enable_memoization", True)
    # i18n.set("error_on_missing_translation", True)
    i18n.set("skip_locale_root_data", True)  # IMPORTANT
    i18n.set("locale", GlobalConfig.language)


def set_language(language: str, update_config: bool = True):
    i18n.set("locale", language)
    if update_config:
        GlobalConfig.language = language
        GlobalConfig.save()


def get_language() -> str:
    return i18n.get("locale")


_init_i18n()

t = i18n.t
