from py_multitasking import Event, TaskContext

from .workloads_distributor import distribute_evenly
from .page_iterator import (
    PageIterator,
    ALL_PAGES,
    ODD_PAGES,
    EVEN_PAGES,
    LAST_PAGE,
    InvalidPageRangeError,
)
from .name_generator import NameGenerator, FilterFunc


def check_cancel_event(ctx: TaskContext | None) -> bool:
    return ctx is not None and ctx.has_cancel_event() and ctx.is_cancel_event_set()


__all__ = [
    "distribute_evenly",
    "PageIterator",
    "ALL_PAGES",
    "ODD_PAGES",
    "EVEN_PAGES",
    "LAST_PAGE",
    "InvalidPageRangeError",
    "NameGenerator",
    "FilterFunc",
    "check_cancel_event",
]
