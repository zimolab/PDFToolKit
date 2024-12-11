from importlib import resources
from importlib.resources import as_file
from os import PathLike
from pathlib import Path

_PACKAGE_NAME = "pdftoolkit"
_ASSETS_DIR_NAME = "assets"
_IMAGE_DIR_NAME = "images"
_LOCALES_DIR_NAME = "locales"
_LICENSE_FILE_NAME = "LICENSE.txt"


def assets_dir() -> Path:
    with as_file(resources.files(_PACKAGE_NAME).joinpath(_ASSETS_DIR_NAME)) as path:
        return path


def locales_dir() -> Path:
    return assets_dir() / _LOCALES_DIR_NAME


def images_dir() -> Path:
    return assets_dir() / _IMAGE_DIR_NAME


def assets_file(filename: PathLike | str) -> Path:
    return assets_dir() / filename


def locales_file(filename: PathLike | str) -> Path:
    return locales_dir() / filename


def license_file() -> Path:
    return assets_file(_LICENSE_FILE_NAME)
