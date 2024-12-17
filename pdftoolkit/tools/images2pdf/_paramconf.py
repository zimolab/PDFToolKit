from pyguiadapter.widgets import FileListEditConfig, FileSelectConfig, ChoiceBoxConfig

from ._commons import _this_t, _DUPLICATE_POLICY_CONFIRM, _DUPLICATE_POLICIES
from ..commons.paramconf import PARAM_WORKER_COUNT, PARAM_VERBOSE, PARAM_OPEN_OUTPUT_DIR
from ...translation import param_name_t, tools_t


DEFAULT_IMAGE_FILES = []
DEFAULT_DEST_FILE = "output.pdf"
DEFAULT_DUPLICATE_POLICY = _DUPLICATE_POLICY_CONFIRM

CONFIGS = {
    "image_files": FileListEditConfig(
        label=param_name_t("image_files"),
        default_value=DEFAULT_IMAGE_FILES,
        add_file_button_text=_this_t("add_file_button_text"),
        remove_button_text=_this_t("remove_button_text"),
        clear_button_text=_this_t("clear_button_text"),
        file_filters=tools_t("image_file_filters"),
        height=350,
    ),
    "dest_file": FileSelectConfig(
        label=param_name_t("dest_file"),
        default_value=DEFAULT_DEST_FILE,
        filters=tools_t("pdf_file_filters"),
    ),
    "duplicate_policy": ChoiceBoxConfig(
        label=param_name_t("duplicate_policy"),
        default_value=DEFAULT_DUPLICATE_POLICY,
        choices=_DUPLICATE_POLICIES,
    ),
    "worker_count": PARAM_WORKER_COUNT,
    "verbose": PARAM_VERBOSE,
    "open_output_dir": PARAM_OPEN_OUTPUT_DIR,
}
