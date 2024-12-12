from pyguiadapter.adapter import GUIAdapter

from . import _paramconf, _winconf
from ._commons import _this_t
from ._impl import pdf2images
from ...assets import locales_file
from ...translation import tools_t
from ...utils import read_asset_text_file

FUNC_GROUP_NAME = tools_t("group_converters")
FUNC_CANCELLABLE = True
FUNC_ICON = "fa5.images"
FUNC_DISPLAY_NAME = _this_t("display_name")
FUNC_DOCUMENT = (
    read_asset_text_file(locales_file(_this_t("document_file")))
    or "Documentation not found!"
)
FUNC_DOCUMENT_FORMAT = "html"


def use(adapter: GUIAdapter):
    adapter.add(
        pdf2images,
        group=FUNC_GROUP_NAME,
        cancelable=FUNC_CANCELLABLE,
        display_name=FUNC_DISPLAY_NAME,
        document=FUNC_DOCUMENT,
        document_format=FUNC_DOCUMENT_FORMAT,
        icon=FUNC_ICON,
        widget_configs=_paramconf.CONFIGS,
        window_config=_winconf.CONFIG,
    )
