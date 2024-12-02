from pathlib import Path

from pyguiadapter.exceptions import ParameterError

from .basic import ensure_non_empty_string


def ensure_path_exists(parameter_name: str, filepath: str):
    ensure_non_empty_string(parameter_name, filepath)
    path = Path(filepath)
    if not path.exists():
        raise ParameterError(parameter_name, "file not found")


def ensure_dir_exists(parameter_name: str, directory: str):
    ensure_non_empty_string(parameter_name, directory)
    path = Path(directory)
    if not path.is_dir():
        raise ParameterError(parameter_name, "directory not found")


def ensure_file_exists(parameter_name: str, filepath: str):
    ensure_non_empty_string(parameter_name, filepath)
    path = Path(filepath)
    if not path.is_file():
        raise ParameterError(parameter_name, "file not found")
