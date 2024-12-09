import dataclasses
import datetime
import os
import subprocess
import sys


from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Generator, Union, Type

from pyguiadapter.adapter import uoutput, ucontext


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


def makedirs(dirpath: Union[str, Path]):
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


def read_file(
    filepath: str, encoding: str = "utf-8", no_raise: bool = True
) -> Optional[str]:
    try:
        with open(filepath, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        if no_raise:
            print(f"Error reading file {filepath}: {e}", file=sys.stderr)
            return None
        else:
            raise e


def write_file(
    filepath: str, content: str, encoding: str = "utf-8", no_raise: bool = True
):
    try:
        with open(filepath, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        if no_raise:
            print(f"Error writing file {filepath}: {e}", file=sys.stderr)
        else:
            raise e


def show_in_file_manager(file_path: str):
    try:
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":
            subprocess.call(["open", file_path])
        else:
            subprocess.call(["xdg-open", file_path])
    except Exception as e:
        print(f"Error showing file in file manager: {e}", file=sys.stderr)


def get_cup_count() -> int:
    return os.cpu_count() or 1


def get_username() -> Optional[str]:
    return os.getlogin() or None


def dataclass_to_dict(obj: object) -> dict:
    return {k: v for k, v in obj.__dict__.items() if not k.startswith("_")}


def dataclass_from_dict(data: dict, clazz: Type[dataclasses.dataclass]) -> dataclass:
    fields = {f.name for f in dataclasses.fields(clazz) if not f.name.startswith("_")}
    copied = {k: v for k, v in data.items() if k in fields}
    for k in data.keys():
        if k not in fields:
            copied.pop(k)
    return clazz(**copied)


def timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
