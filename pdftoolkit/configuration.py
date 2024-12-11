"""
This module contains the implementation of the AppConfig class, which is used to store and retrieve application
configurations. A global instance of AppConfig is created in this module and can be accessed anywhere in the code.

@author: zimolab
@created: 2024-12-11
"""

import dataclasses
import json
from os import PathLike
from pathlib import Path

from . import logme
from .externals import APP_DATA_DIR
from .utils import (
    dataclass_to_dict,
    dataclass_from_dict,
    write_text_file,
    read_text_file,
)

_DEFAULT_CONFIG_FILE = "config.json"
_DEFAULT_LANGUAGE_MAP = {
    "en_US": "English",
    "zh_CN": "简体中文",
}
_VALID_THEMES = ("auto", "light", "dark")

APP_CONFIG_FILEPATH = APP_DATA_DIR / _DEFAULT_CONFIG_FILE
DEFAULT_LANGUAGE = "zh_CN"
DEFAULT_THEME = "auto"

_L = logme.new(__name__)


@dataclasses.dataclass
class AppConfig(object):
    language: str = DEFAULT_LANGUAGE
    theme: str = DEFAULT_THEME
    first_run: bool = True
    language_map: dict[str, str] | None = None

    def save(self, filepath: PathLike | str = APP_CONFIG_FILEPATH):
        try:
            config_dict = dataclass_to_dict(self)
            config_json = json.dumps(config_dict, indent=4, ensure_ascii=False)
            write_text_file(
                file_path=filepath,
                content=config_json,
                encoding="utf-8",
                no_raise=False,
            )
            _L.debug(f"config saved")
        except Exception as e:
            _L.error(f"failed to save config: {e}")

    @classmethod
    def load(cls, filepath: PathLike | str = APP_CONFIG_FILEPATH) -> "AppConfig":
        path = Path(filepath)
        # create default config file if not exist
        if not path.is_file():
            return cls.restore_default(filepath)
        try:
            config_json = read_text_file(filepath, encoding="utf-8", no_raise=False)
            return dataclass_from_dict(json.loads(config_json), cls)
        except Exception as e:
            _L.error(f"failed to load config: {e}")
            # restore default config if load failed
            return cls.restore_default(filepath)

    @classmethod
    def restore_default(cls, filepath=APP_CONFIG_FILEPATH) -> "AppConfig":
        default_config = cls()
        default_config.save(filepath)
        return default_config


def is_valid_theme(theme: str) -> bool:
    return theme in _VALID_THEMES


def get_theme_safely(theme: str) -> tuple[str, bool]:
    if theme not in _VALID_THEMES:
        return DEFAULT_THEME, False
    return theme, True


def get_language_map(user_lang_map: dict[str, str]) -> dict[str, str]:
    if not user_lang_map:
        return _DEFAULT_LANGUAGE_MAP.copy()
    lang_map = _DEFAULT_LANGUAGE_MAP.copy()
    for lang_code, lang_name in user_lang_map.items():
        if lang_code in lang_map:
            continue
        lang_map[lang_code] = lang_name
    return lang_map


GlobalConfig = AppConfig.load()
