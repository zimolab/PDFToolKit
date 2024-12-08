"""
A tool used to make a PDF file from a set of images.

@author: zimolab
@date: 2024-12-03
"""

import gc
import time
from dataclasses import dataclass
from typing import Optional, List, Tuple

import pymupdf
from py_multitasking import TaskContext, with_process_pool_executor, Scopes, Scope
from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.adapter.ucontext import is_function_cancelled
from pyguiadapter.adapter.uoutput import uprint
from pyguiadapter.adapter.uprogress import (
    show_progressbar,
    hide_progressbar,
    update_progress,
)
from pyguiadapter.exceptions import ParameterError
from pyguiadapter.extend_types import file_t, file_list_t
from pyguiadapter.widgets import DictEditConfig
from pyguiadapter.windows import DocumentBrowserConfig
from pyguiadapter.windows.fnexec import FnExecuteWindowConfig, OutputBrowserConfig

from ..commons.app_meta import APP_NAME
from ..commons.app_translation import t
from ..commons.ui.window import (
    DEFAULT_WINDOW_SIZE,
    DEFAULT_OUTPUT_BROWSER_FONT_SIZE,
    DEFAULT_DOCUMENT_BROWSER_FONT_SIZE,
    DEFAULT_OUTPUT_BROWSER_HEIGHT,
)
from ..commons.utils import get_cup_count, close_safely, get_username
from ..commons.validators.basic import ensure_non_empty_string, ensure_in_range
from ..core.workloads_distributor import distribute_evenly


DEFAULT_IMAGES = ""
DEFAULT_OUTPUT_FILE = "$indir/output/output.pdf"
DEFAULT_WORKER_COUNT = 1
DEFAULT_METADATA = {
    "producer": APP_NAME,
    "author": get_username() or APP_NAME,
    "keywords": "",
    "creationDate": "",
    "modDate": "",
    "subject": "",
    "title": "",
    "format": "PDF 1.6",
    "creator": APP_NAME,
    "trapped": "",
    "encryption": None,
}


@dataclass
class ImageData(object):
    page_index: Optional[int] = None
    page_bytes: Optional[bytes] = None
    page_rect: Optional[pymupdf.Rect] = None
    exception: Optional[Exception] = None


def populate_image_data(ctx: TaskContext, images: List[Tuple[int, str]]):
    for i, image_filepath in images:
        result = ImageData(page_index=i)
        img_doc = None
        try:
            # check if cancel event has been set
            # if so, exit the loop to stop the task
            if ctx.has_cancel_event() and ctx.is_cancel_event_set():
                if img_doc:
                    close_safely(img_doc)
                break
            # read image file and convert to PDF bytes
            img_doc = pymupdf.open(image_filepath)
            result.page_rect = img_doc[0].rect
            result.page_bytes = img_doc.convert_to_pdf()
            # write result to output queue
            # this will be read by the main process
            if ctx.has_output_queue():
                ctx.write_output(result)
        except Exception as e:
            result.exception = e
            if ctx.has_output_queue():
                ctx.write_output(result)
        finally:
            if img_doc:
                close_safely(img_doc)


def make_blank_document(page_count: int) -> pymupdf.Document:
    doc = pymupdf.Document()
    for i in range(page_count):
        doc.insert_page(i)
    return doc


def replace_page(
    doc: pymupdf.Document, page_index: int, page_bytes: bytes, page_rect: pymupdf.Rect
):
    page_doc = pymupdf.open("pdf", page_bytes)
    doc.delete_page(page_index)
    page = doc.new_page(page_index, width=page_rect.width, height=page_rect.height)
    page.show_pdf_page(page_rect, page_doc, 0)
    close_safely(page_doc)


def images2pdf(
    images: file_list_t, output_file: file_t, worker_count: int, metadata: dict
):
    """Convert a set of images to a PDF file.

    :param images: A list of image file paths.
    :param output_file: The output PDF file path.
    :param worker_count: The number of worker processes. More workers may speed up the process, but may consume more memory.
    :param metadata: The metadata of the generated PDF file.
    :return:
    """
    if not images:
        raise ParameterError("images", "no images provided")
    ensure_non_empty_string("output_file", output_file)
    ensure_in_range(
        "worker_count",
        worker_count,
        minimum=1,
        maximum=get_cup_count(),
        include_minimum=True,
        include_maximum=True,
    )

    start_time = time.time_ns()

    doc = make_blank_document(len(images))
    images_items = [(i, filepath) for i, filepath in enumerate(images)]
    total = len(images_items)
    finished = 0
    try:
        processing_error = None
        with with_process_pool_executor(max_workers=worker_count) as manager:
            scopes = Scopes.Null()
            scopes.output_queue = Scope.Session
            scopes.cancel_event = Scope.Session
            workloads = distribute_evenly(images_items, worker_count)
            session = manager.map("task-", populate_image_data, scopes, workloads)
            show_progressbar(max_value=total, min_value=0)
            while not session.all_done:
                if is_function_cancelled():
                    uprint("Canceling...")
                    session.cancel_all(with_cancel_event_set=True)
                    session.wait_for_all()
                    # empty the output queue
                    _ = session.context.read_output_until_empty()
                    session.destroy()
                    close_safely(doc)
                    gc.collect()
                    uprint("Cancelled.")
                    hide_progressbar()
                    return

                image_datas = session.context.read_output_until_empty()
                if not image_datas:
                    continue
                for image_data in image_datas:
                    image_data: ImageData
                    # handle successful image data population
                    if image_data.exception is None:
                        replace_page(
                            doc,
                            page_index=image_data.page_index,
                            page_bytes=image_data.page_bytes,
                            page_rect=image_data.page_rect,
                        )
                        uprint(f"Page {image_data.page_index + 1} added to the PDF")
                        finished += 1
                        update_progress(finished)
                        continue
                    # handle exception during populating image data
                    uprint(
                        f"Error processing page {image_data.page_index + 1}: {image_data.exception}"
                    )
                    processing_error = image_data.exception
                    # cancel all remaining tasks
                    session.cancel_all(with_cancel_event_set=True)
                    break

            if processing_error is not None:
                # wait for all tasks to exit
                session.wait_for_all()
                # empty the output queue
                _ = session.context.read_output_until_empty()
                session.destroy()
                raise processing_error
            else:
                # read all remaining output(if any)
                image_datas = session.context.read_output_until_empty()
                for image_data in image_datas:
                    image_data: ImageData
                    if image_data.exception is not None:
                        uprint(
                            f"Error processing page {image_data.page_index + 1}: {image_data.exception}"
                        )
                        session.destroy()
                        raise image_data.exception
                    replace_page(
                        doc,
                        page_index=image_data.page_index,
                        page_bytes=image_data.page_bytes,
                        page_rect=image_data.page_rect,
                    )
                    finished += 1
                    update_progress(finished)
                    uprint(f"Page {image_data.page_index + 1} added to the PDF")
                session.destroy()
    except Exception as e:
        hide_progressbar()
        close_safely(doc)
        gc.collect()
        raise e

    hide_progressbar()

    try:
        if metadata:
            doc.set_metadata(metadata)
        doc.ez_save(output_file)
    except Exception as e:
        uprint(f"Error saving PDF file: {e}")
        raise e
    else:
        uprint(f"PDF file saved to {output_file}")
        uprint(f"Time taken: {(time.time_ns() - start_time) / 1e9:.3f} seconds")
    finally:
        close_safely(doc)
        gc.collect()


# ----------------------------------Below are the window and widgets configuration codes--------------------------------
_T = "app.tools"

FUNC_DISPLAY_NAME = "Images to PDF"
FUNC_GROUP_NAME = t(f"{_T}.group_converters")

PARAM_GROUP_MAIN = "Main"
PARAM_GROUP_METADATA = "Metadata"
PARAM_GROUP_MISC = "Misc"

EXEC_WINDOW_CONFIG = FnExecuteWindowConfig(
    title=FUNC_DISPLAY_NAME,
    size=DEFAULT_WINDOW_SIZE,
    output_browser_config=OutputBrowserConfig(
        font_size=DEFAULT_OUTPUT_BROWSER_FONT_SIZE
    ),
    document_browser_config=DocumentBrowserConfig(
        font_size=DEFAULT_DOCUMENT_BROWSER_FONT_SIZE
    ),
    execute_button_text="Start",
    default_parameter_group_name=PARAM_GROUP_MAIN,
    print_function_result=False,
    print_function_error=False,
    output_dock_initial_size=(None, DEFAULT_OUTPUT_BROWSER_HEIGHT),
)

WIDGET_CONFIGS = {
    "metadata": DictEditConfig(
        label="Metadata",
        group=PARAM_GROUP_METADATA,
        default_value=DEFAULT_METADATA,
        height=253,
    )
}

# --------------------------------Add the function to GUIAdapter instance------------------------------------------------


def use(adapter: GUIAdapter):
    adapter.add(
        images2pdf,
        cancelable=True,
        display_name=FUNC_DISPLAY_NAME,
        group=FUNC_GROUP_NAME,
        # document=FUNC_DOCUMENT,
        # document_format=FUNC_DOCUMENT_FORMAT,
        # icon=FUNC_ICON,
        widget_configs=WIDGET_CONFIGS,
        window_config=EXEC_WINDOW_CONFIG,
    )
