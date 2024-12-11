from typing import Optional

from pyguiadapter.exceptions import ParameterError


def ensure_string(parameter_name: str, value: str, msg: Optional[str] = None):
    msg = msg or f"{parameter_name} should be a string"
    if not isinstance(value, str):
        raise ParameterError(parameter_name, msg)


def ensure_non_empty_string(parameter_name: str, value: str, msg: Optional[str] = None):
    msg = msg or f"{parameter_name} should be a non-empty string"
    ensure_string(parameter_name, value)
    if not value.strip():
        raise ParameterError(parameter_name, msg)


def ensure_in_range(
    parameter_name: str,
    value: int,
    minimum: Optional[int],
    maximum: Optional[int],
    include_minimum=True,
    include_maximum=False,
    msg: Optional[str] = None,
):
    if not isinstance(value, (int, float)):
        msg = msg or f"{parameter_name} should be a number"
        raise ParameterError(parameter_name, msg)
    msg = msg or f"{parameter_name} should be in range {minimum} to {maximum}"
    if (
        minimum is not None
        and value < minimum
        or (not include_minimum and value == minimum)
    ):
        raise ParameterError(parameter_name, msg)
    if (
        maximum is not None
        and value > maximum
        or (not include_maximum and value == maximum)
    ):
        raise ParameterError(parameter_name, msg)
