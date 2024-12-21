"""
This module provides a parameter widget named PDFItemListView which is a list view for holding PDFItem objects.

A `PDFItem` is a named tuple with two fields: `file_path` and `page_ranges`.

@author: zimolab
@created: 2024-12-11
"""

from typing import NamedTuple, Any, Type, Optional

from qtpy.QtWidgets import QWidget
from pyguiadapter.widgets import CommonParameterWidgetConfig, CommonParameterWidget


class PDFItem(NamedTuple):
    file_path: str
    page_ranges: str


class PDFItemListViewConfig(CommonParameterWidgetConfig):

    @classmethod
    def target_widget_class(cls) -> Type["CommonParameterWidget"]:
        return PDFItemListView


class PDFItemListView(CommonParameterWidget):
    ConfigClass = PDFItemListViewConfig

    def __init__(
        self,
        parent: Optional[QWidget],
        parameter_name: str,
        config: PDFItemListViewConfig,
    ):
        super().__init__(parent, parameter_name, config)

    @property
    def value_widget(self) -> QWidget:
        pass

    def set_value_to_widget(self, value: Any) -> None:
        pass

    def get_value_from_widget(self) -> Any:
        pass
