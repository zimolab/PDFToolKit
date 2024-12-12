from pyguiadapter.widgets import FileListEditConfig, FileSelectConfig, ChoiceBoxConfig

from pdftoolkit.tools.images2pdf._commons import (
    _this_t,
    DUPLICATE_POLICY_ON_OVERWRITE,
    DUPLICATE_POLICY_OVERWRITE,
    DUPLICATE_POLICY_CONFIRM,
)
from pdftoolkit.translation import param_name_t

_IMG_FILTERS = ""

_DEPLICATE_POLICIES = {
    _this_t("duplicate_no_overwrite"): DUPLICATE_POLICY_ON_OVERWRITE,
    _this_t("duplicate_overwrite"): DUPLICATE_POLICY_OVERWRITE,
    _this_t("duplicate_confirm"): DUPLICATE_POLICY_CONFIRM,
}

CONFIGS = {
    "image_files": FileListEditConfig(
        label=param_name_t("image_files"),
        add_file_button_text=_this_t("add_file_button_text"),
        remove_button_text=_this_t("remove_button_text"),
        clear_button_text=_this_t("clear_button_text"),
    ),
    "dest_file": FileSelectConfig(
        label=param_name_t("dest_file"),
    ),
    "duplicate_policy": ChoiceBoxConfig(
        label=param_name_t("duplicate_policy"), choices=_DEPLICATE_POLICIES
    ),
}
