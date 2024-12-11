"""
External paths used by PDF Toolkit application.

@author: zimolab
@created: 2024-12-11
"""

from pathlib import Path

from platformdirs import user_data_dir


APP_DATA_DIR = Path(
    user_data_dir(
        appname="pdftoolkit",
        appauthor=False,
        version=None,
        roaming=False,
        ensure_exists=True,
    )
)

APP_LOG_DIR = APP_DATA_DIR / "logs"
