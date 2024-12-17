"""
This module contains some common stuffs related to parameter configurations,which can be used by any tools, including:
- Common parameter group name constants, naming in format: PARAM_GROUP_<group_name_in_uppercase>
- Common parameter default values, naming in format: DEFAULT_<param_name_in_uppercase>
- Common parameter configurations, naming in format: PARAM_<param_name_in_uppercase>
- Common constants, like MIN_WORKER_COUNT, MAX_WORKER_COUNT, etc.

@author: zimolab
@created: 2024-12-13
"""

from pyguiadapter.widgets import IntSpinBoxConfig, BoolBoxConfig

from ...translation import param_name_t, tools_t
from ...utils import cpu_count

# Some constants used in common parameter configurations
MIN_WORKER_COUNT = 1
MAX_WORKER_COUNT = cpu_count(MIN_WORKER_COUNT)

# Common parameter group names
# constant name format: PARAM_GROUP_<group_name_in_uppercase>
# group name of advanced parameters
PARAM_GROUP_ADVANCED = tools_t(f"param_group_advanced")
# group name of miscellaneous parameters
PARAM_GROUP_MISC = tools_t(f"param_group_misc")

# Common parameter default values
# constant name format: DEFAULT_<param_name_in_uppercase>
# default value of parameter 'worker_count'
DEFAULT_WORKER_COUNT = MIN_WORKER_COUNT
# default value of parameter 'verbose'
DEFAULT_VERBOSE = True
# default value of parameter 'open_output_dir'
DEFAULT_OPEN_OUTPUT_DIR = True

# Common parameter configurations
# constant name format: PARAM_<param_name_in_uppercase>
# configuration of parameter 'worker_count'
PARAM_WORKER_COUNT = IntSpinBoxConfig(
    label=param_name_t("worker_count"),
    default_value=DEFAULT_WORKER_COUNT,
    min_value=MIN_WORKER_COUNT,
    step=1,
    max_value=MAX_WORKER_COUNT,
    group=PARAM_GROUP_MISC,
)
# configuration of parameter 'verbose'
PARAM_VERBOSE = BoolBoxConfig(
    label=param_name_t("verbose"),
    default_value=DEFAULT_VERBOSE,
    true_text=tools_t("enabled"),
    false_text=tools_t("disabled"),
    group=PARAM_GROUP_MISC,
)
# configuration of parameter 'open_output_dir'
PARAM_OPEN_OUTPUT_DIR = BoolBoxConfig(
    label=param_name_t("open_output_dir"),
    default_value=DEFAULT_OPEN_OUTPUT_DIR,
    true_text=tools_t("yes"),
    false_text=tools_t("no"),
    group=PARAM_GROUP_MISC,
)
