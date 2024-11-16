from pyguiadapter.window import SimpleWindowEventListener
from pyguiadapter.windows.fnselect import FnSelectWindow


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
