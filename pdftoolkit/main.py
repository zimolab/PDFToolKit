import pymupdf
from pyguiadapter.adapter import GUIAdapter

from pdftoolkit.configs import (
    SELECT_WINDOW_CONFIG,
    SELECT_WINDOW_LISTENER,
    SELECT_WINDOW_MENUS,
)
from pdftoolkit.core.page_iterator import PageIterator


def add(a: int, b: int):
    return a + b


def main():
    adapter = GUIAdapter()
    adapter.add(add)
    adapter.run(
        show_select_window=True,
        select_window_config=SELECT_WINDOW_CONFIG,
        select_window_listener=SELECT_WINDOW_LISTENER,
        select_window_menus=SELECT_WINDOW_MENUS,
    )


if __name__ == "__main__":
    main()