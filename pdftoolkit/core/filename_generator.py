import inspect
import os
from string import Template
from typing import Dict, Any, Callable, Union, Mapping

FilterFunc = Callable[[Dict[str, Any]], str]


class FilenameGenerator(object):
    def __init__(
        self,
        context: Dict[str, Union[Any, FilterFunc]] = None,
        sys_env: bool = True,
    ):
        if context is None:
            context = {}
        self._sys_env = sys_env
        self._context = {**context}

    def update_context(self, varname: str, value: Union[Any, FilterFunc]):
        self._context[varname] = value

    def clear_context(self):
        self._context.clear()

    @staticmethod
    def _finalize_variable(
        context: Dict[str, Any], value: Union[Any, FilterFunc]
    ) -> Any:
        if callable(value):
            signature = inspect.signature(value)
            if len(signature.parameters) == 0:
                return value()
            else:
                return value(context)

        return value

    def _finalize_context(self) -> Dict[str, Any]:
        context = self._context.copy()
        for key, value in context.items():
            context[key] = self._finalize_variable(context, value)
        return context

    def _get_sys_env(self) -> Mapping[str, str]:
        if not self._sys_env:
            return {}
        return os.environ.copy()

    def generate(self, filename_pattern: str, safe: bool = True) -> str:
        context = self._finalize_context()
        sys_env = self._get_sys_env()
        filename_template = Template(filename_pattern)
        if safe:
            return filename_template.safe_substitute(context, **sys_env)
        else:
            return filename_template.substitute(context, **sys_env)
