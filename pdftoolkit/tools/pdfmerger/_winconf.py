import dataclasses

from ._commons import _this_t
from ..commons.winconf import DEFAULT_EXEC_WINDOW_CONFIG

CONFIG = dataclasses.replace(DEFAULT_EXEC_WINDOW_CONFIG, title=_this_t("pdfmerger"))
