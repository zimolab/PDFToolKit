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
from pyguiadapter.adapter.ucontext import is_function_cancelled
from pyguiadapter.adapter.uprogress import (
    show_progressbar,
    update_progress,
    hide_progressbar,
)
from pyguiadapter.extend_types import file_t, directory_t
from pymupdf import TOOLS

from ._paramconf import (
    DuplicatePolicy,
    DEFAULT_INPUT_FILE,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_FILENAME_FORMAT,
    DEFAULT_DUPLICATE_POLICY,
    DEFAULT_PAGE_RANGES,
    DEFAULT_DPI,
    DEFAULT_ALPHA,
    DEFAULT_ROTATION,
    DEFAULT_COLORSPACE,
    DEFAULT_ANNOTS,
    DEFAULT_WORKER_COUNT,
    DEFAULT_VERBOSE,
    DEFAULT_OPEN_OUTPUT_DIR,
)
from ..commons.context import runtime, dtime, rand
from ..commons.name_generator import NameGenerator
from ..commons.page_iterator import ALL_PAGES, PageIterator
from ..commons.validators import (
    ensure_non_empty_string,
    ensure_in_range,
    ensure_file_exists,
)
from ..commons.workloads_distributor import distribute_evenly
from ...utils import (
    pprint,
    open_in_file_manager,
    cwd,
    makedirs,
    close_safely,
)


class Operation(enum.Enum):
    Created = "created"
    Overwritten = "overwritten"
    Skipped = "skipped"
    Errored = "errored"


WORKER_COUNT_BY_CPU_COUNT = -256
FALLBACK_WORKER_COUNT = 1

MIN_DPI = 72
MAX_DPI = 7000

MIN_ROTATION = 0
MAX_ROTATION = 360


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


def build_context(input_file_path: Path, page_count: int) -> Dict[str, Any]:
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


def gen_output_paths(
    page_indexes: List[int],
    filename_generator: NameGenerator,
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
            # noinspection PyUnresolvedReferences
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

    filename_context = build_context(input_file_path, page_count)
    filename_generator = NameGenerator(filename_context)
    output_dir = filename_generator.generate(output_dir)
    output_dirpath = Path(output_dir).absolute().as_posix()
    makedirs(output_dirpath)
    output_filepaths = gen_output_paths(
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
            open_in_file_manager(output_dirpath)

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
