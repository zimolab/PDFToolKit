import dataclasses
import json
import sys
from pathlib import Path
from typing import Tuple, Dict, Optional

from .app_path import APP_EXT_HOME_DIR
from .utils import dataclass_to_dict, dataclass_from_dict, write_file, read_file

APP_CONFIG_FILEPATH = Path(APP_EXT_HOME_DIR).joinpath("config.json")

DEFAULT_LANGUAGE = "zh_CN"
DEFAULT_THEME = "auto"

DEFAULT_LANGUAGE_MAP = {
    "en_US": "English",
    "zh_CN": "简体中文",
}

ALLOWED_THEMES = ("auto", "light", "dark")


@dataclasses.dataclass
class AppConfig(object):
    language: str = DEFAULT_LANGUAGE
    theme: str = DEFAULT_THEME
    first_run: bool = True
    language_map: Optional[Dict[str, str]] = None

    def save(self, filepath=APP_CONFIG_FILEPATH):
        try:
            config_dict = dataclass_to_dict(self)
            config_json = json.dumps(config_dict, indent=4, ensure_ascii=False)
            write_file(
                filepath=filepath.absolute().as_posix(),
                content=config_json,
                encoding="utf-8",
                no_raise=False,
            )
        except Exception as e:
            print(
                f"Failed to save app config to {filepath}: {e}",
                flush=True,
                file=sys.stderr,
            )

    @classmethod
    def load(cls, filepath=APP_CONFIG_FILEPATH) -> "AppConfig":
        path = Path(filepath)
        # create default config file if not exist
        if not path.is_file():
            return cls.restore_default(filepath)
        try:
            config_json = read_file(
                filepath.absolute().as_posix(), encoding="utf-8", no_raise=False
            )
            return dataclass_from_dict(json.loads(config_json), cls)
        except Exception as e:
            print(
                f"Failed to load app config from {filepath}: {e}",
                flush=True,
                file=sys.stderr,
            )
            # restore default config if load failed
            return cls.restore_default(filepath)

    @classmethod
    def restore_default(cls, filepath=APP_CONFIG_FILEPATH) -> "AppConfig":
        default_config = cls()
        default_config.save(filepath)
        return default_config


def get_theme_safely(theme: str) -> Tuple[str, bool]:
    if theme not in ALLOWED_THEMES:
        return DEFAULT_THEME, False
    return theme, True


def get_language_map(user_lang_map: Dict[str, str]) -> Dict[str, str]:
    if not user_lang_map:
        return DEFAULT_LANGUAGE_MAP.copy()
    lang_map = DEFAULT_LANGUAGE_MAP.copy()
    for lang_code, lang_name in user_lang_map.items():
        if lang_code in lang_map:
            continue
        lang_map[lang_code] = lang_name
    return lang_map


GlobalConfig = AppConfig.load()
