from pathlib import Path
from typing import Optional

from pyguiadapter.exceptions import ParameterError

from .basic import ensure_non_empty_string


def ensure_path_exists(parameter_name: str, filepath: str, msg: Optional[str] = None):
    ensure_non_empty_string(parameter_name, filepath)
    path = Path(filepath)
    if not path.exists():
        msg = msg or "path not found"
        raise ParameterError(parameter_name, msg)


def ensure_dir_exists(parameter_name: str, directory: str, msg: Optional[str] = None):
    ensure_non_empty_string(parameter_name, directory)
    path = Path(directory)
    if not path.is_dir():
        msg = msg or "directory not found"
        raise ParameterError(parameter_name, msg)


def ensure_file_exists(parameter_name: str, filepath: str, msg: Optional[str] = None):
    ensure_non_empty_string(parameter_name, filepath)
    path = Path(filepath)
    if not path.is_file():
        msg = msg or "file not found"
        raise ParameterError(parameter_name, msg)
