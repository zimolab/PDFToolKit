import qtmodern.styles
from pyguiadapter.widgets import ParameterWidgetFactory
from pyguiadapter.widgets.factory import ParameterWidgetRegistry

from qtpy.QtWidgets import QApplication
from pyguiadapter.adapter import GUIAdapter

from pdftoolkit.common_configs import (
    SELECT_WINDOW_CONFIG,
    SELECT_WINDOW_LISTENER,
    SELECT_WINDOW_MENUS,
)
from pdftoolkit.converters import pdf2images, images2pdf
from pdftoolkit.rect_widget import rect_tuple_t, RectWidget


def register_custom_widgets():
    ParameterWidgetFactory.register(rect_tuple_t, RectWidget)


def on_app_start(app: QApplication):
    qtmodern.styles.light(app)


def main():
    register_custom_widgets()
    adapter = GUIAdapter(on_app_start=on_app_start)
    adapter.add(
        pdf2images.pdf2images,
        group=pdf2images.GROUP,
        icon=pdf2images.ICON,
        display_name=pdf2images.DISPLAY_NAME,
        cancelable=pdf2images.CANCELABLE,
        window_config=pdf2images.WINDOW_CONFIG,
        widget_configs=pdf2images.WIDGET_CONFIGS,
    )
    adapter.add(
        images2pdf.images2pdf, icon=images2pdf.ICON, group=images2pdf.GROUP_NAME
    )
    adapter.run(
        show_select_window=True,
        select_window_config=SELECT_WINDOW_CONFIG,
        select_window_listener=SELECT_WINDOW_LISTENER,
        select_window_menus=SELECT_WINDOW_MENUS,
    )


if __name__ == "__main__":
    main()
