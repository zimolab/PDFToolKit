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
from pdftoolkit.tools import pdf2images, images2pdf


def register_custom_widgets():
    ParameterWidgetFactory.register(rect_tuple_t, RectWidget)


def on_app_start(app: QApplication):
    qtmodern.styles.light(app)


def main():
    register_custom_widgets()
    adapter = GUIAdapter(on_app_start=on_app_start)
    pdf2images.use(adapter)
    images2pdf.use(adapter)
    adapter.run(
        show_select_window=True,
        select_window_config=SELECT_WINDOW_CONFIG,
        select_window_listener=SELECT_WINDOW_LISTENER,
        select_window_menus=SELECT_WINDOW_MENUS,
    )


if __name__ == "__main__":
    main()
