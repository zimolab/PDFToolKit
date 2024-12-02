from pyguiadapter.action import Separator
from pyguiadapter.menu import Menu

from .actions import ACTION_ABOUT, ACTION_HOMEPAGE, ACTION_LICENSE

MENU_HELP = Menu(
    title="Help", actions=[ACTION_ABOUT, Separator(), ACTION_HOMEPAGE, ACTION_LICENSE]
)
