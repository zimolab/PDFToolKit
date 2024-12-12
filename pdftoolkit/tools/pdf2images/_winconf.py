from pyguiadapter.windows import DocumentBrowserConfig
from pyguiadapter.windows.fnexec import FnExecuteWindowConfig, OutputBrowserConfig

from ._commons import _this_t
from ..commons.winconf import (
    DEFAULT_WINDOW_SIZE,
    DEFAULT_OUTPUT_FONT_SIZE,
    DEFAULT_OUTPUT_FONT_FAMILY,
    DEFAULT_DOCUMENT_FONT_SIZE,
    DEFAULT_DOCUMENT_FONT_FAMILY,
    DEFAULT_OUTPUT_DOCK_HEIGHT,
)
from ...translation import tools_t

CONFIG = FnExecuteWindowConfig(
    size=DEFAULT_WINDOW_SIZE,
    # translatable texts
    title=_this_t("display_name"),
    execute_button_text=tools_t("execute_button_text"),
    cancel_button_text=tools_t("cancel_button_text"),
    clear_button_text=tools_t("clear_button_text"),
    clear_checkbox_text=tools_t("clear_checkbox_text"),
    output_dock_title=tools_t("output_dock_title"),
    document_dock_title=tools_t("document_dock_title"),
    default_parameter_group_name=tools_t("param_group_main"),
    # text browser configs
    output_browser_config=OutputBrowserConfig(
        font_size=DEFAULT_OUTPUT_FONT_SIZE, font_family=DEFAULT_OUTPUT_FONT_FAMILY
    ),
    document_browser_config=DocumentBrowserConfig(
        font_size=DEFAULT_DOCUMENT_FONT_SIZE,
        font_family=DEFAULT_DOCUMENT_FONT_FAMILY,
        parameter_anchor=True,
    ),
    # dock configs
    output_dock_initial_size=(None, DEFAULT_OUTPUT_DOCK_HEIGHT),
    # other configs
    print_function_error=False,
    print_function_result=False,
)
