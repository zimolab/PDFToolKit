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

from ..commons import ALL_PAGES, ODD_PAGES, EVEN_PAGES
from ...translation import param_name_t, tools_t
from ...utils import cpu_count


class DuplicatePolicy(enum.Enum):
    Skip = "skip"
    Overwrite = "overwrite"


CS_RGB = "RGB"
CS_GRAY = "GRAY"
CS_CMYK = "CMYK"


WORKER_COUNT_BY_CPU_COUNT = -256
FALLBACK_WORKER_COUNT = 1

MIN_DPI = 72
MAX_DPI = 7000

MIN_ROTATION = 0
MAX_ROTATION = 360

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
DEFAULT_WORKER_COUNT = 1
DEFAULT_VERBOSE = True
DEFAULT_OPEN_OUTPUT_DIR = True

FILE_FILTERS = "PDF files (*.pdf);;All files (*.*)"

PARAM_GROUP_ADVANCED = tools_t("param_group_advanced")
PARAM_GROUP_MISC = tools_t(f"param_group_misc")


CONFIGS = {
    "input_file": FileSelectConfig(
        label=param_name_t("input_file"),
        default_value=DEFAULT_INPUT_FILE,
        filters=FILE_FILTERS,
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
            "All Pages": ALL_PAGES,
            "Odd Pages": ODD_PAGES,
            "Even Pages": EVEN_PAGES,
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
        true_text="Enabled",
        false_text="Disabled",
        group=PARAM_GROUP_ADVANCED,
    ),
    "rotation": IntSpinBoxConfig(
        label=param_name_t("rotation"),
        default_value=DEFAULT_ROTATION,
        default_value_description="No rotation",
        min_value=0,
        max_value=360,
        step=90,
        group=PARAM_GROUP_ADVANCED,
    ),
    "colorspace": ExclusiveChoiceBoxConfig(
        label=param_name_t("colorspace"),
        default_value=DEFAULT_COLORSPACE,
        default_value_description="Auto",
        choices=[CS_RGB, CS_GRAY, CS_CMYK],
        group=PARAM_GROUP_ADVANCED,
    ),
    "annots": BoolBoxConfig(
        label=param_name_t("annots"),
        default_value=DEFAULT_ANNOTS,
        true_text="Render",
        false_text="Suppress",
        group=PARAM_GROUP_ADVANCED,
    ),
    "worker_count": IntSpinBoxConfig(
        label=param_name_t("worker_count"),
        default_value=DEFAULT_WORKER_COUNT,
        min_value=1,
        step=1,
        max_value=cpu_count(),
        group=PARAM_GROUP_MISC,
    ),
    "verbose": BoolBoxConfig(
        label=param_name_t("verbose"),
        default_value=DEFAULT_VERBOSE,
        true_text="Enabled",
        false_text="Disabled",
        group=PARAM_GROUP_MISC,
    ),
    "open_output_dir": BoolBoxConfig(
        label=param_name_t("open_output_dir"),
        default_value=DEFAULT_OPEN_OUTPUT_DIR,
        true_text="Yes",
        false_text="No",
        group=PARAM_GROUP_MISC,
    ),
}
