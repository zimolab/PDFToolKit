import dataclasses
from typing import Any, Optional, Type, Literal, Tuple

from qtpy.QtCore import Qt
from qtpy.QtWidgets import QWidget, QSpinBox, QDoubleSpinBox, QLabel, QGridLayout
from pyguiadapter.widgets import CommonParameterWidgetConfig, CommonParameterWidget


# noinspection PyPep8Naming
class rect_tuple_t(tuple):
    pass


@dataclasses.dataclass(frozen=True)
class RectWidgetConfig(CommonParameterWidgetConfig):

    default_value: Optional[
        Tuple[float, float, float, float] | Tuple[int, int, int, int]
    ] = (0, 0, 0, 0)
    element_type: Literal["float", "int"] = "int"
    max_value: Optional[int | float] = 2147483647
    min_value: Optional[int | float] = 0
    step: Optional[int | float] = 1
    decimals: int = 2
    labels: Tuple[str, str, str, str] = ("X", "Y", "Width", "Height")
    prefixes: Optional[Tuple[str, str, str]] = None
    suffixes: Optional[Tuple[str, str, str]] = None
    compact_layout: bool = False

    @classmethod
    def target_widget_class(cls) -> Type["RectWidget"]:
        return RectWidget


class RectWidget(CommonParameterWidget):

    ConfigClass = RectWidgetConfig

    def __init__(
        self, parent: Optional[QWidget], parameter_name: str, config: RectWidgetConfig
    ):
        super().__init__(parent, parameter_name, config)
        self._value_widget: Optional[QWidget] = None
        self._ele0_widget: Optional[QSpinBox | QDoubleSpinBox] = None
        self._ele1_widget: Optional[QSpinBox | QDoubleSpinBox] = None
        self._ele2_widget: Optional[QSpinBox | QDoubleSpinBox] = None
        self._ele3_widget: Optional[QSpinBox | QDoubleSpinBox] = None

    @property
    def value_widget(self) -> QWidget:
        self._config: RectWidgetConfig
        if self._value_widget is None:
            self._value_widget = QWidget(self)

            self._ele0_widget = self._create_element_widget(0)
            ele0_label = QLabel(self._value_widget)
            ele0_label.setText(self._config.labels[0])
            ele0_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self._ele1_widget = self._create_element_widget(1)
            ele1_label = QLabel(self._value_widget)
            ele1_label.setText(self._config.labels[1])
            ele1_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self._ele2_widget = self._create_element_widget(2)
            ele2_label = QLabel(self._value_widget)
            ele2_label.setText(self._config.labels[2])
            ele2_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            self._ele3_widget = self._create_element_widget(3)
            ele3_label = QLabel(self._value_widget)
            ele3_label.setText(self._config.labels[3])
            ele3_label.setAlignment(Qt.AlignmentFlag.AlignLeft)

            if self._config.prefixes:
                self._ele0_widget.setPrefix(self._config.prefixes[0])
                self._ele1_widget.setPrefix(self._config.prefixes[1])
                self._ele2_widget.setPrefix(self._config.prefixes[2])

            if self._config.suffixes:
                self._ele0_widget.setSuffix(self._config.suffixes[0])
                self._ele1_widget.setSuffix(self._config.suffixes[1])
                self._ele2_widget.setSuffix(self._config.suffixes[2])

            layout = QGridLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

            if self._config.compact_layout:
                # element 0
                layout.addWidget(ele0_label, 0, 0)
                layout.addWidget(self._ele0_widget, 0, 1)

                # element 1
                layout.addWidget(ele1_label, 0, 2)
                layout.addWidget(self._ele1_widget, 0, 3)

                # element 2
                layout.addWidget(ele2_label, 1, 0)
                layout.addWidget(self._ele2_widget, 1, 1)

                # element 3
                layout.addWidget(ele3_label, 1, 2)
                layout.addWidget(self._ele3_widget, 1, 3)
            else:
                # element 0
                layout.addWidget(ele0_label, 0, 0)
                layout.addWidget(self._ele0_widget, 0, 1, 1, 3)
                # element 1
                layout.addWidget(ele1_label, 1, 0)
                layout.addWidget(self._ele1_widget, 1, 1, 1, 3)
                # element 2
                layout.addWidget(ele2_label, 2, 0)
                layout.addWidget(self._ele2_widget, 2, 1, 1, 3)
                # element 3
                layout.addWidget(ele3_label, 3, 0)
                layout.addWidget(self._ele3_widget, 3, 1, 1, 3)

            self._value_widget.setLayout(layout)

        return self._value_widget

    def check_value_type(self, value: Any):
        if value is None:
            return
        if not isinstance(value, tuple):
            raise TypeError(f"invalid value type: {type(value)}")
        if len(value) != 4:
            raise ValueError(f"invalid value length: {len(value)}")

    def set_value_to_widget(
        self, value: Tuple[int, int, int, int] | Tuple[float, float, float, float]
    ) -> None:
        if not value:
            return
        self._ele0_widget.setValue(value[0])
        self._ele1_widget.setValue(value[1])
        self._ele2_widget.setValue(value[2])
        self._ele3_widget.setValue(value[3])

    def get_value_from_widget(
        self,
    ) -> Tuple[int, int, int, int] | Tuple[float, float, float, float]:
        return (
            self._ele0_widget.value(),
            self._ele1_widget.value(),
            self._ele2_widget.value(),
            self._ele3_widget.value(),
        )

    def _create_element_widget(self, index: int):
        self._config: RectWidgetConfig
        default_value = self._config.default_value
        if default_value is None:
            element_value = None
        else:
            element_value = default_value[index]

        if self._config.element_type == "int":
            element_widget = QSpinBox(self._value_widget)
        else:
            element_widget = QDoubleSpinBox(self._value_widget)
            element_widget.setDecimals(self._config.decimals)

        element_widget.setMinimum(self._config.min_value)
        element_widget.setMaximum(self._config.max_value)
        element_widget.setSingleStep(self._config.step)

        if element_value is not None:
            element_widget.setValue(element_value)

        return element_widget
