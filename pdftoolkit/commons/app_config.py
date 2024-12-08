import dataclasses
import json
import sys
from pathlib import Path

from .app_path import APP_EXT_HOME_DIR
from .utils import dataclass_to_dict, dataclass_from_dict

APP_CONFIG_FILEPATH = Path(APP_EXT_HOME_DIR).joinpath("config.json")

DEFAULT_LANGUAGE = "zh_CN"
DEFAULT_THEME = "default"

DEFAULT_LANGUAGE_MAP = {
    "en_US": "English",
    "zh_CN": "简体中文",
}


def _language_map() -> dict:
    pass


@dataclasses.dataclass
class AppConfig(object):
    language: str = DEFAULT_LANGUAGE
    theme: str = DEFAULT_THEME
    first_run: bool = True
    language_map: dict = dataclasses.field(default_factory=_language_map)

    def save(self, filepath=APP_CONFIG_FILEPATH):
        try:
            with open(filepath, "w") as f:
                config_dict = dataclass_to_dict(self)
                config_json = json.dumps(config_dict, indent=4, ensure_ascii=False)
                f.write(config_json)
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
            # load config from config file
            with open(filepath, "r") as f:
                config_json = f.read()
                config_dict = json.loads(config_json)
                return dataclass_from_dict(config_dict, cls)
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


GlobalConfig = AppConfig.load()
