import os
from pathlib import Path

from pyguiadapter.adapter import uoutput, ucontext


def pprint(
    *args,
    sep: str = " ",
    end: str = "\n",
    html: bool = False,
    scroll_to_bottom: bool = True,
    verbose: bool = False,
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
