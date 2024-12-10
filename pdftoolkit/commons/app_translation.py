from pathlib import Path
from typing import Optional

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


_init_i18n()


def t(key: str, prefix: Optional[str] = None, **kwargs):
    full_key = key
    if prefix:
        full_key = f"{prefix}.{key}"
    return i18n.t(full_key, **kwargs)


def app_t(key: str, prefix: Optional[str] = "app", **kwargs):
    return t(key, prefix, **kwargs)


def select_win_t(key: str, prefix: Optional[str] = "app.select_window", **kwargs):
    return t(key, prefix, **kwargs)


def tools_t(key: str, prefix: Optional[str] = "app.tools", **kwargs):
    return t(key, prefix, **kwargs)


def param_name_t(
    param_name: str, prefix: Optional[str] = "app.param_names", **kwargs
) -> str:
    return t(param_name, prefix, **kwargs)
