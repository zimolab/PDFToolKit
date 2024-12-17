from pyguiadapter.adapter import GUIAdapter

from . import _winconf, _paramconf
from ._commons import _this_t
from ._impl import images2pdf
from ...translation import tools_t


def use(adapter: GUIAdapter):
    adapter.add(
        images2pdf,
        cancelable=True,
        display_name=_this_t("files2pdf"),
        group=tools_t("group_converters"),
        # document=FUNC_DOCUMENT,
        # document_format=FUNC_DOCUMENT_FORMAT,
        # icon=FUNC_ICON,
        widget_configs=_paramconf.CONFIGS,
        window_config=_winconf.CONFIG,
    )
