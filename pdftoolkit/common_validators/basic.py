from pyguiadapter.exceptions import ParameterError


def ensure_string(parameter_name: str, value: str):
    if not isinstance(value, str):
        raise ParameterError(parameter_name, "not a string")


def ensure_non_empty_string(parameter_name: str, value: str):
    ensure_string(parameter_name, value)
    if not value.strip():
        raise ParameterError(parameter_name, "empty string")
