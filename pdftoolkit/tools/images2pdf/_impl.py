import gc
import time
from concurrent.futures import CancelledError
from pathlib import Path
from typing import Sequence

import pymupdf
from py_multitasking import with_process_pool_executor, Scopes, TaskSession
from pyguiadapter.adapter.ucontext import is_function_cancelled
from pyguiadapter.adapter.uprogress import (
    show_progressbar,
    hide_progressbar,
    update_progress,
)
from pyguiadapter.extend_types import file_list_t, file_t

from ._commons import (
    _DUPLICATE_POLICY_CONFIRM,
    _DUPLICATE_POLICIES,
    _blank_document,
    _process_page_images,
    _ImageData,
    _replace_page,
    _cleanup_session,
    _build_name_context,
    _process_duplicate_dest_file,
)
from ..commons import NameGenerator, distribute_evenly
from ..commons.paramconf import (
    DEFAULT_WORKER_COUNT,
    DEFAULT_VERBOSE,
    DEFAULT_OPEN_OUTPUT_DIR,
)
from ..commons.validators import (
    ensure_non_empty_sequence,
    ensure_in_sequence,
    ensure_in_range,
    ensure_non_empty_string,
)
from ...utils import makedirs, close_safely, pprint, open_in_file_manager


def _main_loop(
    session: TaskSession,
    doc: pymupdf.Document,
    total: int,
    save_path: Path | str,
    verbose: bool,
):
    finished = 0
    show_progressbar(max_value=total, min_value=0)
    try:
        pprint("Start processing...", verbose=verbose)
        while not session.all_done:
            if is_function_cancelled():
                raise CancelledError()

            image_datas: Sequence[_ImageData] = (
                session.context.read_output_until_empty()
            )
            if not image_datas:
                continue

            for image_data in image_datas:
                finished += 1
                update_progress(finished)
                if image_data.exception:
                    pprint(
                        f"Error processing page {image_data.index+1}: {image_data.exception}",
                        verbose=verbose,
                    )
                    raise image_data.exception
                _replace_page(doc, image_data)
                pprint(f"Page processed: {image_data.index+1}...", verbose=verbose)

        # read remaining output
        image_datas: Sequence[_ImageData] = session.context.read_output_until_empty()
        for image_data in image_datas:
            finished += 1
            update_progress(finished)
            if image_data.exception:
                pprint(
                    f"Error processing page {image_data.index + 1}: {image_data.exception}",
                    verbose=verbose,
                )
                raise image_data.exception
            _replace_page(doc, image_data)
            pprint(f"Page processed: {image_data.index + 1}...", verbose=verbose)
        # save the document
        save_path = Path(save_path)
        doc.ez_save(save_path)
        pprint(f"PDF saved: {save_path.absolute().as_posix()}", verbose=verbose)
    except CancelledError:
        _cleanup_session(session)
        pprint("Cancelled by user", verbose=verbose)
    except Exception as e:
        _cleanup_session(session)
        pprint(f"Processing failed because an error is occurred: {e}", verbose=verbose)
        raise e


def images2pdf(
    image_files: file_list_t,
    dest_file: file_t,
    duplicate_policy: int = _DUPLICATE_POLICY_CONFIRM,
    worker_count: int = DEFAULT_WORKER_COUNT,
    verbose: bool = DEFAULT_VERBOSE,
    open_output_dir: bool = DEFAULT_OPEN_OUTPUT_DIR,
):
    ensure_non_empty_string("dest_file", dest_file)
    ensure_non_empty_sequence("image_files", image_files)
    ensure_in_sequence(
        "duplicate_policy", duplicate_policy, list(_DUPLICATE_POLICIES.values())
    )
    ensure_in_range("worker_count", worker_count, 1, None)

    start_time = time.time_ns()

    image_count = len(image_files)
    filename_context = _build_name_context(image_count)
    filename_generator = NameGenerator(filename_context)
    dest_file_path = Path(filename_generator.generate(dest_file))
    if not _process_duplicate_dest_file(dest_file_path, duplicate_policy):
        return
    # make sure the output directory exists
    makedirs(dest_file_path.parent)

    image_items = [(i, filepath) for i, filepath in enumerate(image_files)]
    doc = None
    exception = None
    try:
        # make blank pdf document with the same page count as the image count
        doc = _blank_document(image_count)
        with with_process_pool_executor(max_workers=worker_count) as manager:
            scopes = Scopes.Session()
            workloads = distribute_evenly(image_items, worker_count)
            session = manager.map("task-", _process_page_images, scopes, workloads)
            _main_loop(
                session,
                doc=doc,
                total=image_count,
                save_path=dest_file_path,
                verbose=verbose,
            )
    except Exception as e:
        exception = e
    finally:
        time_elapsed = (time.time_ns() - start_time) / 1e9
        hide_progressbar()
        pprint(f"Time elapsed: {time_elapsed:.3f} seconds", verbose=verbose)
        if doc:
            close_safely(doc)
        gc.collect()
        if exception:
            raise exception
        if open_output_dir:
            open_in_file_manager(dest_file_path.parent)
        pymupdf.TOOLS.store_shrink(100)
