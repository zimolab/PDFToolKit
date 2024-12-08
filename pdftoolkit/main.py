import qtmodern.styles
from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.widgets import ParameterWidgetFactory
from qtpy.QtWidgets import QApplication

from pdftoolkit.commons.app_config import GlobalConfig
from pdftoolkit.commons.ui.rect_widget import RectWidget, rect_tuple_t
from pdftoolkit.commons.utils import timestamp
from pdftoolkit.select_window.config import (
    SELECT_WINDOW_CONFIG,
    SELECT_WINDOW_LISTENER,
    SELECT_WINDOW_MENUS,
)
from pdftoolkit.tools import pdf2images, images2pdf, pdfsplitters


def process_first_run():
    if GlobalConfig.first_run:
        print(f"({timestamp()}) First run detected, processing...")
        GlobalConfig.first_run = False
        GlobalConfig.save()


def register_custom_widgets():
    ParameterWidgetFactory.register(rect_tuple_t, RectWidget)


def on_app_start(app: QApplication):
    qtmodern.styles.light(app)


def main():
    process_first_run()
    register_custom_widgets()
    adapter = GUIAdapter(on_app_start=on_app_start)
    pdf2images.use(adapter)
    images2pdf.use(adapter)
    pdfsplitters.use(adapter)
    adapter.run(
        show_select_window=True,
        select_window_config=SELECT_WINDOW_CONFIG,
        select_window_listener=SELECT_WINDOW_LISTENER,
        select_window_menus=SELECT_WINDOW_MENUS,
    )
    GlobalConfig.save()


if __name__ == "__main__":
    main()
