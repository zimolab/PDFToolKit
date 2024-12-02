import qtmodern.styles
from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.widgets import ParameterWidgetFactory
from qtpy.QtWidgets import QApplication

from pdftoolkit.commons.ui.rect_widget import RectWidget, rect_tuple_t
from pdftoolkit.select_window.config import (
    SELECT_WINDOW_CONFIG,
    SELECT_WINDOW_LISTENER,
    SELECT_WINDOW_MENUS,
)
from pdftoolkit.tools import pdf2images


def register_custom_widgets():
    ParameterWidgetFactory.register(rect_tuple_t, RectWidget)


def on_app_start(app: QApplication):
    qtmodern.styles.light(app)


def main():
    register_custom_widgets()
    adapter = GUIAdapter(on_app_start=on_app_start)
    adapter.add(
        pdf2images.pdf2images,
        cancelable=pdf2images.FUNC_CANCELLABLE,
        display_name=pdf2images.FUNC_DISPLAY_NAME,
        document=pdf2images.FUNC_DOCUMENT,
        document_format=pdf2images.FUNC_DOCUMENT_FORMAT,
        icon=pdf2images.FUNC_ICON,
        widget_configs=pdf2images.WIDGET_CONFIGS,
        window_config=pdf2images.EXEC_WINDOW_CONFIG,
    )
    adapter.run(
        show_select_window=True,
        select_window_config=SELECT_WINDOW_CONFIG,
        select_window_listener=SELECT_WINDOW_LISTENER,
        select_window_menus=SELECT_WINDOW_MENUS,
    )


if __name__ == "__main__":
    main()
