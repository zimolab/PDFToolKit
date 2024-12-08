from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.extend_types import file_t, directory_t


def split_pdf_evenly_by_page_count(
    input_file: file_t,
    output_dir: directory_t,
    pages_per_file: int,
    filename_format: str,
):
    pass


def split_pdf_evenly_by_file_count(
    input_file: file_t,
    output_dir: directory_t,
    file_count: int,
    filename_format: str,
):
    pass


# ----------------------------------Below are the window and widgets configuration codes--------------------------------

FUNC_GROUP_NAME = "Splitters"


# --------------------------------Add the function to GUIAdapter instance------------------------------------------------
def use(adapter: GUIAdapter):
    adapter.add(
        split_pdf_evenly_by_page_count,
        group=FUNC_GROUP_NAME,
        # cancelable=FUNC_CANCELLABLE,
        # display_name=FUNC_DISPLAY_NAME,
        # document=FUNC_DOCUMENT,
        # document_format=FUNC_DOCUMENT_FORMAT,
        # icon=FUNC_ICON,
        # widget_configs=WIDGET_CONFIGS,
        # window_config=EXEC_WINDOW_CONFIG,
    )
    adapter.add(
        split_pdf_evenly_by_file_count,
        group=FUNC_GROUP_NAME,
        # cancelable=FUNC_CANCELLABLE,
        # display_name=FUNC_DISPLAY_NAME,
        # document=FUNC_DOCUMENT,
        # document_format=FUNC_DOCUMENT_FORMAT,
        # icon=FUNC_ICON,
        # widget_configs=WIDGET_CONFIGS,
        # window_config=EXEC_WINDOW_CONFIG,
    )
