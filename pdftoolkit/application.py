"""
The entry point of the pdftoolkit application.

@author: zimolab
@created: 2024-12-11
"""

import qdarktheme
from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.widgets import ParameterWidgetFactory
from qtpy.QtWidgets import QApplication

from pdftoolkit.widgets import rect_tuple_t, RectWidget
from pdftoolkit import logme
from pdftoolkit.configuration import GlobalConfig, get_theme_safely
from pdftoolkit.tools import select_window, pdfmerger
from pdftoolkit.tools import pdf2images
from pdftoolkit.tools import images2pdf
from pdftoolkit.utils import unused

_L = logme.new(__name__)


def register_parameter_widgets():
    ParameterWidgetFactory.register(rect_tuple_t, RectWidget)


def on_app_start(app: QApplication):
    unused(app)
    theme, ok = get_theme_safely(GlobalConfig.theme)
    if not ok:
        GlobalConfig.theme = theme
        GlobalConfig.save()
    qdarktheme.setup_theme(theme)


def process_first_run():
    if GlobalConfig.first_run:
        _L.info("application is running for the first time")
        GlobalConfig.first_run = False
        GlobalConfig.save()


def main():
    _L.info("application started")
    register_parameter_widgets()
    # process first run if necessary
    process_first_run()
    adapter = GUIAdapter(on_app_start=on_app_start)
    pdf2images.use(adapter)
    images2pdf.use(adapter)
    pdfmerger.use(adapter)
    adapter.run(
        show_select_window=True,
        select_window_config=select_window.WINDOW_CONFIG,
        select_window_listener=select_window.WINDOW_LISTENER,
        select_window_menus=select_window.WINDOW_MENUS,
    )
    # always save the config before exiting
    GlobalConfig.save()
    _L.info("application exited")


if __name__ == "__main__":
    main()
