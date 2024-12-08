from pathlib import Path

from platformdirs import user_data_dir

CURRENT_DIR = Path(__file__).parent.absolute().as_posix()
PACKAGE_ROOT = Path(CURRENT_DIR).parent.absolute().as_posix()
ASSETS_DIR = Path(PACKAGE_ROOT).joinpath("assets").as_posix()

APP_EXT_HOME_DIR = (
    Path(
        user_data_dir(
            appname="pdftoolkit",
            appauthor=False,
            version=None,
            roaming=False,
            ensure_exists=True,
        )
    )
    .absolute()
    .as_posix()
)
