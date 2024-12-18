from pyguiadapter.adapter import GUIAdapter

from . import _winconf
from ._commons import _this_t
from ._impl import pdfmerger
from ...translation import tools_t


def use(adapter: GUIAdapter):
    adapter.add(
        pdfmerger,
        cancelable=True,
        display_name=_this_t("display_name"),
        group=tools_t("group_merger_and_spliter"),
        # document=FUNC_DOCUMENT,
        # document_format=FUNC_DOCUMENT_FORMAT,
        # icon=FUNC_ICON,
        # widget_configs=_paramconf.CONFIGS,
        window_config=_winconf.CONFIG,
    )
