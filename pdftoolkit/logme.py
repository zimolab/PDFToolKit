"""
This module provides logging functionalities.

@author: zimolab
@created: 2024-12-11
"""

import sys

from loguru import logger

from pdftoolkit.externals import APP_LOG_DIR

_LOG_FORMAT = "{time:YYYY-MM-DD HH:mm:ss.SSS} |<lvl>{level:8}</>| {name} : {module}:{line:4} | <cyan>{extra[module_name]}</> | - <lvl>{message}</>"
_DEFAULT_LOG_FILE = APP_LOG_DIR / "app.log"
_MAX_LOG_SIZE = "10 MB"

logger.configure(
    handlers=[
        {
            "sink": sys.stderr,
            "format": _LOG_FORMAT,
            "colorize": True,
        },
        {
            "sink": _DEFAULT_LOG_FILE,
            "format": _LOG_FORMAT,
            "colorize": False,
            "rotation": _MAX_LOG_SIZE,
        },
    ]
)


def new(module_name: str) -> logger:
    return logger.bind(module_name=module_name)
