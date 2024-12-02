from typing import Optional

from pyguiadapter.exceptions import ParameterError


def ensure_string(parameter_name: str, value: str):
    if not isinstance(value, str):
        raise ParameterError(parameter_name, "not a string")


def ensure_non_empty_string(parameter_name: str, value: str):
    ensure_string(parameter_name, value)
    if not value.strip():
        raise ParameterError(parameter_name, "empty string")


def ensure_in_range(
    parameter_name: str,
    value: int,
    minimum: Optional[int],
    maximum: Optional[int],
    include_minimum=True,
    include_maximum=False,
):
    if not isinstance(value, (int, float)):
        raise ParameterError(parameter_name, "not a number")
    if (
        minimum is not None
        and value < minimum
        or (not include_minimum and value == minimum)
    ):
        raise ParameterError(parameter_name, f"less than {minimum}")
    if (
        maximum is not None
        and value > maximum
        or (not include_maximum and value == maximum)
    ):
        raise ParameterError(parameter_name, f"greater than {maximum}")
