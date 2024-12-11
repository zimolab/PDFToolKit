"""
This module contains utility functions can be accessed by other modules.

@author: zimolab
@created: 2024-12-11
"""

import dataclasses
import os
import subprocess
import sys
from datetime import datetime
from os import PathLike
from pathlib import Path
from typing import Any, Type, Sequence, Optional, Generator

from pyguiadapter.adapter import ucontext, uoutput

from .assets import assets_file


def read_text_file(
    file_path: PathLike | str, encoding: str = "utf-8", no_raise: bool = False
) -> str | None:
    """
    Read the content of a text file.

    Args:
        file_path (PathLike): The path of the text file.
        encoding (str, optional): The encoding of the text file. Defaults to 'utf-8'.
        no_raise (bool, optional): Whether to raise an exception if any error occurs during reading. Defaults to False.

    Returns:
        Optional[str]: The content of the text file. If reading fails and no_raise is False, None will be returned.
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        if no_raise:
            return None
        else:
            raise e


def write_text_file(
    file_path: PathLike | str,
    content: str,
    encoding: str = "utf-8",
    no_raise: bool = False,
) -> bool:
    """
    Write content to a text file.

    Args:
        file_path (PathLike): The path of the text file.
        content (str): The content to be written to the text file.
        encoding (str, optional): The encoding of the text file. Defaults to 'utf-8'.
        no_raise (bool, optional): Whether to raise an exception if any error occurs during writing. Defaults to False.

    Returns:
        bool: True if writing succeeds, False otherwise.
    """
    try:
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
        return True
    except Exception as e:
        if no_raise:
            return False
        else:
            raise e


def read_asset_text_file(
    asset_file_path: PathLike | str, encoding: str = "utf-8", no_raise: bool = False
):
    """
    Read the content of an asset text file.

    Args:
        asset_file_path (PathLike): The path of the asset text file.
        encoding (str, optional): The encoding of the asset text file. Defaults to 'utf-8'.
        no_raise (bool, optional): Whether to raise an exception if any error occurs during reading. Defaults to False.

    Returns:
        Optional[str]: The content of the asset text file. If reading fails and no_raise is False, None will be returned.
    """
    return read_text_file(
        assets_file(asset_file_path), encoding=encoding, no_raise=no_raise
    )


def open_in_file_manager(file_path: PathLike | str, no_raise: bool = True) -> bool:
    """
    Open the file_path with the default file manager of the system.

    Args:
        file_path (PathLike): The path of the file to be opened in the file manager.
        no_raise (bool, optional): Whether to raise an exception if any error occurs. Defaults to True.

    Returns:
        bool: True if opening succeeds, False (any error raised) otherwise.

    """
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.call(["open", file_path])
        else:
            subprocess.call(["xdg-open", file_path])
        return True
    except Exception as e:
        if no_raise:
            print(f"Error showing file in file manager: {e}", file=sys.stderr)
            return False
        else:
            raise e


def cpu_count(default: int = 1) -> int:
    """
    Get the number of CPUs in the system.

    Args:
        default (int, optional): The default number of CPUs to be returned if the system cannot determine the number of CPUs. Defaults to 1.

    Returns:
        int: The number of CPUs in the system.
    """
    return os.cpu_count() or default


def username(default: str | None = None) -> str | None:
    """
    Get the username of the current user.

    Args:
        default (str, optional): The default username to be returned if the system cannot determine the username. Defaults to None.

    Returns:
        str: The username of the current user.
    """
    return os.getlogin() or default


def dataclass_to_dict(
    obj: dataclasses.dataclass,
    exclude_fields: Sequence[str] | None = None,
    exclude_private_fields: bool = True,
) -> dict:
    """
    Convert a dataclass object to a dictionary.

    Args:
        obj (dataclasses.dataclass): The dataclass object to be converted.
        exclude_fields (Sequence[str], optional): The fields to be excluded from the dictionary. Defaults to None.
        exclude_private_fields (bool, optional): Whether to exclude private fields (starting with '_') from the dictionary. Defaults to True.

    Returns:
        dict: The dictionary representation of the dataclass object.
    """
    if exclude_fields is None:
        return {
            k: v
            for k, v in obj.__dict__.items()
            if (not exclude_private_fields)
            or (exclude_private_fields and not k.startswith("_"))
        }
    else:
        return {
            k: v
            for k, v in obj.__dict__.items()
            if (k not in exclude_fields)
            and (
                (not exclude_private_fields)
                or (exclude_private_fields and not k.startswith("_"))
            )
        }


def dataclass_from_dict(
    data: dict, clazz: Type[dataclasses.dataclass], exclude_private_fields: bool = True
) -> dataclasses.dataclass:
    """
    Create a dataclass object from a dictionary.

    Args:
        data (dict): The dictionary to be converted to a dataclass object.
        clazz (Type[dataclasses.dataclass]): The dataclass type to be created.
        exclude_private_fields (bool, optional): Whether to exclude private fields (starting with '_') from the dictionary. Defaults to True.

    Returns:
        dataclasses.dataclass: The dataclass object created from the dictionary.
    """
    fields = {
        f.name
        for f in dataclasses.fields(clazz)
        if (not exclude_private_fields)
        or (exclude_private_fields and not f.name.startswith("_"))
    }
    copied = {k: v for k, v in data.items() if k in fields}
    for k in data.keys():
        if k not in fields:
            copied.pop(k)
    return clazz(**copied)


def timestamp(strformat: str = "%Y-%m-%d-%H:%M:%S") -> str:
    return datetime.now().strftime(strformat)


def unused(arg: Any):
    _ = arg


def pprint(
    *args,
    sep: str = " ",
    end: str = "\n",
    html: bool = False,
    scroll_to_bottom: bool = True,
    verbose: bool = True,
):
    if not verbose:
        return
    if ucontext.get_current_window() is None:
        print(*args, sep=sep, end=end)
        return
    uoutput.uprint(
        *args, sep=sep, end=end, html=html, scroll_to_bottom=scroll_to_bottom
    )


def cwd() -> str:
    path = Path(os.getcwd())
    return str(path.absolute())


def list_files(
    dir_path: str, filters: str, recursive: bool = False
) -> Optional[Generator[str, None, None]]:
    path = Path(dir_path)
    if not path.is_dir():
        return None
    if not recursive:
        return (str(p.absolute()) for p in path.glob(filters) if p.is_file())
    return (str(p.absolute()) for p in path.rglob(filters) if p.is_file())


def get_file_ext(file_path: str) -> str:
    return os.path.splitext(file_path)[1][1:]


def makedirs(dirpath: PathLike | str):
    dirpath = Path(dirpath)
    if not dirpath.is_dir():
        dirpath.mkdir(parents=True, exist_ok=True)


def close_safely(obj, output_stderr: bool = False):
    if obj is None:
        return
    try:
        obj.close()
    except Exception as e:
        if output_stderr:
            print(f"Error closing {obj}: {e}", file=sys.stderr)
