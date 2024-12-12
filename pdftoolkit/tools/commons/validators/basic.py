from typing import Sequence, Any

from pyguiadapter.exceptions import ParameterError


def ensure_string(parameter_name: str, value: str, msg: str | None = None):
    msg = msg or f"{parameter_name} should be a string"
    if not isinstance(value, str):
        raise ParameterError(parameter_name, msg)


def ensure_non_empty_string(parameter_name: str, value: str, msg: str | None = None):
    msg = msg or f"{parameter_name} should be a non-empty string"
    ensure_string(parameter_name, value)
    if not value.strip():
        raise ParameterError(parameter_name, msg)


def ensure_in_range(
    parameter_name: str,
    value: int,
    minimum: int | None,
    maximum: int | None,
    include_minimum: bool = True,
    include_maximum: bool = False,
    msg: str | None = None,
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


def ensure_non_empty_sequence(
    parameter_name: str, value: Sequence[Any], msg: str | None = None
):
    if len(value) == 0:
        msg = msg or f"{parameter_name} should not be an empty sequence"
        raise ParameterError(parameter_name, msg)


def ensure_in_set(
    parameter_name: str, value: Any, allowed_values: set, msg: str | None = None
):
    if value not in allowed_values:
        msg = msg or f"{parameter_name} should be one of {allowed_values}"
        raise ParameterError(parameter_name, msg)
