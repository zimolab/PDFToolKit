from pyguiadapter.window import SimpleWindowEventListener
from pyguiadapter.windows.fnselect import FnSelectWindowConfig, FnSelectWindow

from ..commons.ui.menus import MENU_HELP
from ..commons.ui.window import DEFAULT_WINDOW_SIZE, DEFAULT_DOCUMENT_BROWSER_WIDTH
from ..commons.constants import APP_NAME

SELECT_WINDOW_CONFIG = FnSelectWindowConfig(
    title=APP_NAME,
    icon="fa5s.file-pdf",
    size=DEFAULT_WINDOW_SIZE,
    document_browser_width=DEFAULT_DOCUMENT_BROWSER_WIDTH,
)


# noinspection PyUnusedLocal
def on_window_create(window: FnSelectWindow):
    pass


# noinspection PyUnusedLocal
def on_window_close(window: FnSelectWindow) -> bool:
    return True


# noinspection PyUnusedLocal
def on_window_show(window: FnSelectWindow):
    pass


# noinspection PyUnusedLocal
def on_window_hide(window: FnSelectWindow):
    pass


# noinspection PyTypeChecker
SELECT_WINDOW_LISTENER = SimpleWindowEventListener(
    on_create=on_window_create,
    on_close=on_window_close,
    on_show=on_window_show,
    on_hide=on_window_hide,
)


SELECT_WINDOW_MENUS = (MENU_HELP,)