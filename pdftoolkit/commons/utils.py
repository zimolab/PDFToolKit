import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Generator, Union

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


def read_file(file_path: str, encoding: str = "utf-8") -> Optional[str]:
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}", file=sys.stderr)
        return None


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
