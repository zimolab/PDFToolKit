from pyguiadapter.adapter import GUIAdapter

from . import _paramconf, _winconf
from ._commons import _this_t
from ._impl import pdf2images
from ...assets import locales_file
from ...translation import tools_t
from ...utils import read_asset_text_file


# FUNC_ICON = "fa5.images"


def use(adapter: GUIAdapter):
    adapter.add(
        pdf2images,
        group=tools_t("group_converters"),
        cancelable=True,
        display_name=_this_t("display_name"),
        document=(
            read_asset_text_file(locales_file(_this_t("document_file")))
            or "Documentation not found!"
        ),
        document_format="html",
        # icon=FUNC_ICON,
        widget_configs=_paramconf.CONFIGS,
        window_config=_winconf.CONFIG,
    )
