import dataclasses

from ..commons.winconf import DEFAULT_EXEC_WINDOW_CONFIG
from ...translation import tools_t

CONFIG = dataclasses.replace(DEFAULT_EXEC_WINDOW_CONFIG, title=tools_t("display_name"))
