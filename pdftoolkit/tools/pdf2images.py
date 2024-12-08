"""
A tool to convert PDF pages to image files.

@author: zimolab
@created: 2024-12-02
"""

import enum
import gc
import os
import time
from dataclasses import dataclass
from functools import partial
from pathlib import Path
from typing import Dict, Optional, Any, List, Tuple

import pymupdf
from py_multitasking import (
    TaskContext,
    with_process_pool_executor,
    Scopes,
    Scope,
    TaskResult,
)
from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.adapter.ucontext import is_function_cancelled
from pyguiadapter.adapter.uprogress import (
    show_progressbar,
    update_progress,
    hide_progressbar,
)
from pyguiadapter.extend_types import file_t, directory_t
from pyguiadapter.widgets import (
    FileSelectConfig,
    DirSelectConfig,
    LineEditConfig,
    ExclusiveChoiceBoxConfig,
    ChoiceBoxConfig,
    IntSpinBoxConfig,
    BoolBoxConfig,
)
from pyguiadapter.windows import DocumentBrowserConfig
from pyguiadapter.windows.fnexec import FnExecuteWindowConfig, OutputBrowserConfig
from pymupdf import TOOLS

from ..commons.app_translation import t, LOCALES_DIR
from ..commons.context_variables import runtime, dtime, rand
from ..commons.ui.window import (
    DEFAULT_WINDOW_SIZE,
    DEFAULT_OUTPUT_BROWSER_HEIGHT,
    DEFAULT_OUTPUT_BROWSER_FONT_SIZE,
    DEFAULT_DOCUMENT_BROWSER_FONT_SIZE,
)
from ..commons.utils import (
    pprint,
    show_in_file_manager,
    read_file,
    cwd,
    makedirs,
    close_safely,
)
from ..commons.validators.basic import ensure_non_empty_string, ensure_in_range
from ..commons.validators.filepath import ensure_file_exists
from ..core.filename_generator import FilenameGenerator
from ..core.page_iterator import ALL_PAGES, PageIterator, ODD_PAGES, EVEN_PAGES
from ..core.workloads_distributor import distribute_evenly


class DuplicatePolicy(enum.Enum):
    Skip = "skip"
    Overwrite = "overwrite"


class Operation(enum.Enum):
    Created = "created"
    Overwritten = "overwritten"
    Skipped = "skipped"
    Errored = "errored"


CS_RGB = "RGB"
CS_GRAY = "GRAY"
CS_CMYK = "CMYK"


WORKER_COUNT_BY_CPU_COUNT = -256
FALLBACK_WORKER_COUNT = 1

MIN_DPI = 72
MAX_DPI = 7000

MIN_ROTATION = 0
MAX_ROTATION = 360

DEFAULT_INPUT_FILE = ""
DEFAULT_OUTPUT_DIR = "$indir/output/"
DEFAULT_FILENAME_FORMAT = "page-$page.png"
DEFAULT_PAGE_RANGES = ALL_PAGES
DEFAULT_DPI = 300
DEFAULT_ALPHA = False
DEFAULT_ROTATION = 0
DEFAULT_COLORSPACE = CS_RGB
DEFAULT_ANNOTS = True
DEFAULT_DUPLICATE_POLICY = DuplicatePolicy.Skip
DEFAULT_WORKER_COUNT = 1
DEFAULT_VERBOSE = True
DEFAULT_OPEN_OUTPUT_DIR = True


@dataclass
class PageMessage(object):
    page_index: Optional[int] = None
    output_path: Optional[str] = None
    operation: Optional[Operation] = None
    error: Optional[Exception] = None


@dataclass
class TaskReturn(object):
    total_count: int = -1
    success_count: int = -1
    failure_count: int = -1
    page_exceptions: Optional[Dict[int, Exception]] = None
    fatal_exception: Optional[Exception] = None


def build_filename_context(input_file_path: Path, page_count: int) -> Dict[str, Any]:
    ctx = {
        **runtime.VARIABLES,
        **dtime.VARIABLES,
        **rand.VARIABLES,
        runtime.VARNAME_TOTAL: page_count,
        runtime.VARNAME_CWD_DIR: cwd(),
        runtime.VARNAME_INPUT_FILENAME: input_file_path.name,
        runtime.VARNAME_INPUT_FILE_DIR: input_file_path.parent.absolute().as_posix(),
    }
    return ctx


def generate_output_filepaths(
    page_indexes: List[int],
    filename_generator: FilenameGenerator,
    output_dirpath: str,
    filename_format: str,
) -> List[Tuple[int, str]]:
    output_files = []
    for page_index in page_indexes:
        cur_page_num = page_index + 1
        filename_generator.update_context(runtime.VARNAME_CUR_INDEX, page_index)
        filename_generator.update_context(runtime.VARNAME_CUR_PAGE, cur_page_num)

        filename = filename_generator.generate(filename_format)
        output_filepath = Path(output_dirpath).joinpath(filename)
        makedirs(output_filepath.parent)
        output_files.append((page_index, output_filepath.as_posix()))

    return output_files


def pdf2images_task(
    ctx: TaskContext,
    output_filepaths: Dict[int, str],
    duplicate_policy: DuplicatePolicy,
    input_file: str,
    dpi: int,
    alpha: bool,
    rotation: int,
    colorspace: str,
    annots: bool,
) -> TaskReturn:
    ret = TaskReturn(
        total_count=len(output_filepaths),
        success_count=0,
        failure_count=0,
        page_exceptions=None,
        fatal_exception=None,
    )

    try:
        document = pymupdf.open(input_file)
    except Exception as e:
        ret.fatal_exception = e
        return ret

    page_exceptions = {}
    page_result = PageMessage()

    for page_index, output_filepath in output_filepaths:
        if ctx and ctx.is_cancel_event_set():
            break

        try:
            page_result.page_index = page_index
            page_result.output_path = output_filepath
            output_filepath = Path(output_filepath)
            if output_filepath.is_file():
                if duplicate_policy == DuplicatePolicy.Skip:
                    page_result.operation = Operation.Skipped
                    ret.success_count = ret.success_count + 1
                    if ctx and ctx.has_output_queue():
                        ctx.write_output(page_result, block=False)
                    continue
                else:
                    page_result.operation = Operation.Overwritten
            else:
                page_result.operation = Operation.Created
            page = document[page_index]
            page.set_rotation(rotation)
            pixmap = page.get_pixmap(
                dpi=dpi,
                alpha=alpha,
                colorspace=colorspace,
                annots=annots,
            )
            pixmap.save(output_filepath)
            ret.success_count = ret.success_count + 1
            del page
            del pixmap
        except Exception as e:
            page_result.operation = Operation.Errored
            page_result.error = e
            page_exceptions[page_index] = e
            ret.failure_count = ret.failure_count + 1

        if ctx and ctx.has_output_queue():
            ctx.write_output(page_result, block=False)

    if page_exceptions:
        ret.page_exceptions = page_exceptions

    close_safely(document)
    TOOLS.store_shrink(100)
    return ret


def pdf2images(
    input_file: file_t = DEFAULT_INPUT_FILE,
    output_dir: directory_t = DEFAULT_OUTPUT_DIR,
    filename_format: str = DEFAULT_FILENAME_FORMAT,
    duplicate_policy: DuplicatePolicy = DEFAULT_DUPLICATE_POLICY,
    page_ranges: str = DEFAULT_PAGE_RANGES,
    dpi: int = DEFAULT_DPI,
    alpha: bool = DEFAULT_ALPHA,
    rotation: int = DEFAULT_ROTATION,
    colorspace: str = DEFAULT_COLORSPACE,
    annots: bool = DEFAULT_ANNOTS,
    worker_count: int = DEFAULT_WORKER_COUNT,
    verbose: bool = DEFAULT_VERBOSE,
    open_output_dir: bool = DEFAULT_OPEN_OUTPUT_DIR,
):
    if worker_count == 0:
        worker_count = FALLBACK_WORKER_COUNT

    if worker_count == WORKER_COUNT_BY_CPU_COUNT:
        worker_count = os.cpu_count() or FALLBACK_WORKER_COUNT

    page_ranges = page_ranges.strip() or ALL_PAGES
    input_file_path = Path(input_file).absolute()

    ensure_file_exists("input_file", input_file_path.as_posix())
    ensure_non_empty_string("filename_format", filename_format)
    ensure_in_range("dpi", dpi, MIN_DPI, MAX_DPI, include_maximum=True)
    ensure_in_range(
        "rotation", rotation, MIN_ROTATION, MAX_ROTATION, include_maximum=True
    )
    ensure_in_range("worker_count", worker_count, 1, maximum=None)

    time_start = time.time_ns()
    try:
        document = pymupdf.open(input_file_path.as_posix())
    except Exception as e:
        raise RuntimeError(f"Failed to open input file: {e}") from e

    page_count = document.page_count
    try:
        page_iterator = PageIterator(page_ranges, document)
        page_indexes = list(page_iterator.page_indexes())
        total_count = len(page_indexes)
    except Exception as e:
        raise RuntimeError(f"Failed to parse page ranges: {e}") from e
    finally:
        close_safely(document)
        TOOLS.store_shrink(100)

    filename_context = build_filename_context(input_file_path, page_count)
    filename_generator = FilenameGenerator(filename_context)
    output_dir = filename_generator.generate(output_dir)
    output_dirpath = Path(output_dir).absolute().as_posix()
    makedirs(output_dirpath)
    output_filepaths = generate_output_filepaths(
        page_indexes=page_indexes,
        filename_generator=filename_generator,
        output_dirpath=output_dirpath,
        filename_format=filename_format,
    )
    # distribute workloads evenly across workers
    work_loads = distribute_evenly(output_filepaths, worker_count)
    with with_process_pool_executor(max_workers=worker_count) as manager:
        show_progressbar(min_value=1, max_value=total_count)
        scopes = Scopes(
            input_queue=Scope.Null,
            output_queue=Scope.Session,
            cancel_event=Scope.Session,
            output_queue_lock=Scope.Session,
        )
        task_func = partial(
            pdf2images_task,
            duplicate_policy=duplicate_policy,
            input_file=input_file_path.as_posix(),
            dpi=dpi,
            alpha=alpha,
            rotation=rotation,
            colorspace=colorspace,
            annots=annots,
        )
        session = manager.map(
            "pdf2images-task-",
            task_func,
            scopes,
            work_loads,
        )

        finished_count = 0

        while True:
            if is_function_cancelled():
                session.cancel_all(with_cancel_event_set=True)
                session.wait_for_all()
                break

            if session.all_done:
                break

            page_results = session.context.read_output_until_empty(block=False)
            for page_result in page_results:
                finished_count += 1
                update_progress(finished_count)
                _print_page_result(page_result, verbose=verbose)

        # read remaining page results from output queue
        page_results = session.context.read_output_until_empty(block=False)
        for page_result in page_results:
            finished_count += 1
            update_progress(finished_count)
            _print_page_result(page_result, verbose=verbose)

        task_results = session.results()
        for task_name, task_result in task_results.items():
            _print_task_result(task_name, task_result, verbose=verbose)

        update_progress(0)
        show_progressbar(min_value=0, max_value=100)
        hide_progressbar()
        time_eclipsed = (time.time_ns() - time_start) / 1e9
        pprint(f"Finished in {time_eclipsed:.2f} seconds", verbose=verbose)

        if open_output_dir:
            show_in_file_manager(output_dirpath)

        gc.collect()


def _print_page_result(page_result: PageMessage, verbose: bool = True):
    if page_result.operation == Operation.Errored:
        pprint(
            f"[Error] page: {page_result.page_index}; error: {page_result.error}",
            verbose=verbose,
        )
    else:
        pprint(
            f"[Success] operation: {page_result.operation}; page: {page_result.page_index}; output: {page_result.output_path}",
            verbose=verbose,
        )


def _print_task_result(task_name: str, task_result: TaskResult, verbose: bool = True):
    if not task_result.successful:
        pprint(f"[Task] {task_name}: {task_result.exception}", verbose=verbose)
        return
    page_task_ret: TaskReturn = task_result.value
    pprint(
        f"[Task] {task_name}: total: {page_task_ret.total_count}; success: {page_task_ret.success_count}; failure: {page_task_ret.failure_count}",
        verbose=verbose,
    )


# ----------------------------------Below are the window and widgets configuration codes--------------------------------

_T = "app.tools"
_P = f"{_T}.pdf2images"

FUNC_DOC_FILE = Path(LOCALES_DIR).joinpath(t(f"{_P}.document_file")).as_posix()

FUNC_GROUP_NAME = t(f"{_T}.group_converters")
FUNC_CANCELLABLE = True
FUNC_ICON = "fa5.images"
FUNC_DISPLAY_NAME = t(f"{_P}.display_name")
FUNC_DOCUMENT = read_file(FUNC_DOC_FILE) or "Documentation not found!"
FUNC_DOCUMENT_FORMAT = "html"

PARAM_GROUP_MAIN = t(f"{_T}.param_group_main")
PARAM_GROUP_ADVANCED = t(f"{_T}.param_group_advanced")
PARAM_GROUP_MISC = t(f"{_T}.param_group_misc")

FILE_FILTERS = "PDF files (*.pdf);;All files (*.*)"

WIDGET_CONFIGS = {
    "input_file": FileSelectConfig(
        label="Input File",
        default_value=DEFAULT_INPUT_FILE,
        filters=FILE_FILTERS,
    ),
    "output_dir": DirSelectConfig(
        label="Output Directory",
        default_value=DEFAULT_OUTPUT_DIR,
    ),
    "filename_format": LineEditConfig(
        label="Filename Format",
        default_value=DEFAULT_FILENAME_FORMAT,
    ),
    "DuplicatePolicy": ExclusiveChoiceBoxConfig(
        label="Duplicate File Policy",
        default_value=DEFAULT_DUPLICATE_POLICY,
    ),
    "page_ranges": ChoiceBoxConfig(
        label="Page Ranges",
        choices={
            "All Pages": ALL_PAGES,
            "Odd Pages": ODD_PAGES,
            "Even Pages": EVEN_PAGES,
        },
        editable=True,
        add_user_input=False,
    ),
    "dpi": IntSpinBoxConfig(
        label="DPI",
        default_value=DEFAULT_DPI,
        min_value=MIN_DPI,
        max_value=MAX_DPI,
        step=50,
        group=PARAM_GROUP_ADVANCED,
    ),
    "alpha": BoolBoxConfig(
        label="Alpha Channel",
        default_value=DEFAULT_ALPHA,
        true_text="Enabled",
        false_text="Disabled",
        group=PARAM_GROUP_ADVANCED,
    ),
    "rotation": IntSpinBoxConfig(
        label="Rotation",
        default_value=DEFAULT_ROTATION,
        default_value_description="No rotation",
        min_value=0,
        max_value=360,
        step=90,
        group=PARAM_GROUP_ADVANCED,
    ),
    "colorspace": ExclusiveChoiceBoxConfig(
        label="Colorspace",
        default_value=DEFAULT_COLORSPACE,
        default_value_description="Auto",
        choices=[CS_RGB, CS_GRAY, CS_CMYK],
        group=PARAM_GROUP_ADVANCED,
    ),
    "annots": BoolBoxConfig(
        label="Annotations",
        default_value=DEFAULT_ANNOTS,
        true_text="Render",
        false_text="Suppress",
        group=PARAM_GROUP_ADVANCED,
    ),
    "worker_count": IntSpinBoxConfig(
        label="Workers",
        default_value=DEFAULT_WORKER_COUNT,
        min_value=1,
        step=1,
        max_value=os.cpu_count() or FALLBACK_WORKER_COUNT,
        group=PARAM_GROUP_MISC,
    ),
    "verbose": BoolBoxConfig(
        label="Verbose",
        default_value=DEFAULT_VERBOSE,
        true_text="Enabled",
        false_text="Disabled",
        group=PARAM_GROUP_MISC,
    ),
    "open_output_dir": BoolBoxConfig(
        label="Open Output Directory",
        default_value=DEFAULT_OPEN_OUTPUT_DIR,
        true_text="Yes",
        false_text="No",
        group=PARAM_GROUP_MISC,
    ),
}

EXEC_WINDOW_CONFIG = FnExecuteWindowConfig(
    title=FUNC_DISPLAY_NAME,
    size=DEFAULT_WINDOW_SIZE,
    output_browser_config=OutputBrowserConfig(
        font_size=DEFAULT_OUTPUT_BROWSER_FONT_SIZE
    ),
    document_browser_config=DocumentBrowserConfig(
        font_size=DEFAULT_DOCUMENT_BROWSER_FONT_SIZE
    ),
    execute_button_text=t(f"{_T}.execute_button_text"),
    cancel_button_text=t(f"{_T}.cancel_button_text"),
    clear_button_text=t(f"{_T}.clear_button_text"),
    clear_checkbox_text=t(f"{_T}.clear_checkbox_text"),
    output_dock_title=t(f"{_T}.output_dock_title"),
    document_dock_title=t(f"{_T}.document_dock_title"),
    default_parameter_group_name=PARAM_GROUP_MAIN,
    print_function_result=False,
    print_function_error=False,
    output_dock_initial_size=(None, DEFAULT_OUTPUT_BROWSER_HEIGHT),
)

# --------------------------------Add the function to GUIAdapter instance------------------------------------------------


def use(adapter: GUIAdapter):
    adapter.add(
        pdf2images,
        group=FUNC_GROUP_NAME,
        cancelable=FUNC_CANCELLABLE,
        display_name=FUNC_DISPLAY_NAME,
        document=FUNC_DOCUMENT,
        document_format=FUNC_DOCUMENT_FORMAT,
        icon=FUNC_ICON,
        widget_configs=WIDGET_CONFIGS,
        window_config=EXEC_WINDOW_CONFIG,
    )
