import enum

from pyguiadapter.widgets import (
    FileSelectConfig,
    DirSelectConfig,
    LineEditConfig,
    EnumSelectConfig,
    ChoiceBoxConfig,
    IntSpinBoxConfig,
    BoolBoxConfig,
    ExclusiveChoiceBoxConfig,
)

from ._commons import _this_t
from ..commons import ALL_PAGES, ODD_PAGES, EVEN_PAGES
from ..commons.paramconf import (
    PARAM_GROUP_ADVANCED,
    PARAM_WORKER_COUNT,
    PARAM_VERBOSE,
    PARAM_OPEN_OUTPUT_DIR,
)
from ...translation import param_name_t, tools_t


class DuplicatePolicy(enum.Enum):
    Skip = "skip"
    Overwrite = "overwrite"


CS_RGB = "RGB"
CS_GRAY = "GRAY"
CS_CMYK = "CMYK"

MIN_DPI = 72
MAX_DPI = 7000
MIN_ROTATION = 0
MAX_ROTATION = 360
ROTATION_STEP = 90

DEFAULT_INPUT_FILE = ""
DEFAULT_OUTPUT_DIR = "$indir/output/"
DEFAULT_FILENAME_FORMAT = "page-$page.png"
DEFAULT_PAGE_RANGES = ALL_PAGES
DEFAULT_DPI = 300
DEFAULT_ALPHA = False
DEFAULT_ROTATION = 0
DEFAULT_COLORSPACE = CS_RGB
DEFAULT_ANNOTS = True
DEFAULT_DUPLICATE_POLICY = DuplicatePolicy.Skip


CONFIGS = {
    "input_file": FileSelectConfig(
        label=param_name_t("input_file"),
        default_value=DEFAULT_INPUT_FILE,
        filters=tools_t("pdf_file_filters"),
    ),
    "output_dir": DirSelectConfig(
        label=param_name_t("output_dir"),
        default_value=DEFAULT_OUTPUT_DIR,
    ),
    "filename_format": LineEditConfig(
        label=param_name_t("filename_format"),
        default_value=DEFAULT_FILENAME_FORMAT,
    ),
    "duplicate_policy": EnumSelectConfig(
        label=param_name_t("duplicate_policy"),
        default_value=DEFAULT_DUPLICATE_POLICY,
    ),
    "page_ranges": ChoiceBoxConfig(
        label=param_name_t("page_ranges"),
        choices={
            _this_t("all_pages"): ALL_PAGES,
            _this_t("odd_pages"): ODD_PAGES,
            _this_t("even_pages"): EVEN_PAGES,
        },
        editable=True,
        add_user_input=False,
    ),
    "dpi": IntSpinBoxConfig(
        label=param_name_t("dpi"),
        default_value=DEFAULT_DPI,
        min_value=MIN_DPI,
        max_value=MAX_DPI,
        step=50,
        group=PARAM_GROUP_ADVANCED,
    ),
    "alpha": BoolBoxConfig(
        label=param_name_t("alpha"),
        default_value=DEFAULT_ALPHA,
        true_text=tools_t("enabled"),
        false_text=tools_t("disabled"),
        group=PARAM_GROUP_ADVANCED,
    ),
    "rotation": IntSpinBoxConfig(
        label=param_name_t("rotation"),
        default_value=DEFAULT_ROTATION,
        min_value=MIN_ROTATION,
        max_value=MAX_ROTATION,
        step=ROTATION_STEP,
        group=PARAM_GROUP_ADVANCED,
    ),
    "colorspace": ExclusiveChoiceBoxConfig(
        label=param_name_t("colorspace"),
        default_value=DEFAULT_COLORSPACE,
        choices=[CS_RGB, CS_GRAY, CS_CMYK],
        group=PARAM_GROUP_ADVANCED,
    ),
    "annots": BoolBoxConfig(
        label=param_name_t("annots"),
        default_value=DEFAULT_ANNOTS,
        true_text=_this_t("render_annots"),
        false_text=_this_t("ignore_annots"),
        group=PARAM_GROUP_ADVANCED,
    ),
    "worker_count": PARAM_WORKER_COUNT,
    "verbose": PARAM_VERBOSE,
    "open_output_dir": PARAM_OPEN_OUTPUT_DIR,
}
