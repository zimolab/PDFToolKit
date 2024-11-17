from pyguiadapter.widgets import FileSelectConfig, ChoiceBoxConfig, LineEditConfig

from ..core.page_iterator import ALL_PAGES, ODD_PAGES, EVEN_PAGES

PAGE_RANGES = ChoiceBoxConfig(
    label="Page Ranges",
    choices={
        "All Pages": ALL_PAGES,
        "Odd Pages": ODD_PAGES,
        "Even Pages": EVEN_PAGES,
    },
    editable=True,
    add_user_input=False,
)
INPUT_FILE = FileSelectConfig()
