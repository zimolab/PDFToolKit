"""
A group of tools to make a PDF file from a set of images.

@author: zimolab
@date: 2024-12-03
"""

import gc
import time
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Sequence

import pymupdf
from py_multitasking import (
    TaskContext,
    with_process_pool_executor,
    Scopes,
    Scope,
    with_thread_pool_executor,
)
from pyguiadapter.adapter import GUIAdapter
from pyguiadapter.exceptions import ParameterError
from pyguiadapter.extend_types import file_t, file_list_t
from pyguiadapter.windows import DocumentBrowserConfig
from pyguiadapter.windows.fnexec import FnExecuteWindowConfig, OutputBrowserConfig

from ..commons.ui.window import (
    DEFAULT_WINDOW_SIZE,
    DEFAULT_OUTPUT_BROWSER_FONT_SIZE,
    DEFAULT_DOCUMENT_BROWSER_FONT_SIZE,
    DEFAULT_OUTPUT_BROWSER_HEIGHT,
)
from ..commons.validators.basic import ensure_non_empty_string
from ..core.workloads_distributor import distribute_evenly


@dataclass
class ImageReadResult(object):
    page_index: Optional[int] = None
    page_bytes: Optional[bytes] = None
    page_rect: Optional[pymupdf.Rect] = None
    exception: Optional[Exception] = None


def read_images(ctx: TaskContext, images: List[Tuple[int, str]]):
    for i, image_filepath in images:
        result = ImageReadResult(page_index=i)
        img_doc = None
        try:
            img_doc = pymupdf.open(image_filepath)
            img_rect = img_doc[0].rect
            result.page_rect = img_rect
            result.page_bytes = img_doc.convert_to_pdf()
            if ctx.has_output_queue():
                ctx.write_output(result)
        except Exception as e:
            result.exception = e
            if ctx.has_output_queue():
                ctx.write_output(result)
        finally:
            if img_doc:
                img_doc.close()


def images2pdf(images: file_list_t, output_file: file_t):
    """
    Convert a set of images to a PDF file.

    :param images:
    :param output_file:
    :return:
    """
    if not images:
        raise ParameterError("images", "no images provided")
    ensure_non_empty_string("output_file", output_file)
    start_time = time.time_ns()
    # image_list = [read_image(image_filepath) for image_filepath in images]
    # image_list[0].save(output_file, "PDF", save_all=True, append_images=image_list[1:])

    # doc = pymupdf.open()  # PDF with the pictures
    #
    # for i, file in enumerate(images):
    #     img = pymupdf.open(file)
    #     rect = img[0].rect
    #     pdfbytes = img.convert_to_pdf()
    #     img.close()
    #     imgpdf = pymupdf.open("pdf", pdfbytes)
    #     page = doc.new_page(width=rect.width, height=rect.height)
    #     page.show_pdf_page(rect, imgpdf, 0)
    # doc.save(output_file)
    # doc.close()

    images_items = [(i, filepath) for i, filepath in enumerate(images)]

    # 创建一个空白的PDF文档
    doc = pymupdf.Document()
    # 创建空白文档
    for i, file in enumerate(images):
        doc.insert_page(i)

    with with_process_pool_executor(max_workers=5) as manager:
        scopes = Scopes.Null()
        scopes.output_queue = Scope.Session
        session = manager.map(
            "task-", read_images, scopes, distribute_evenly(images_items, 5)
        )

        while not session.all_done:
            images_read: Sequence[ImageReadResult] = (
                session.context.read_output_until_empty()
            )
            if not images_read:
                continue
            for result in images_read:
                if result.exception:
                    print(
                        f"Error reading image {result.page_index}: {result.exception}"
                    )
                pdf_bytes = result.page_bytes
                pdf_rect = result.page_rect
                pdf_index = result.page_index
                if pdf_bytes and pdf_rect:
                    img_pdf = pymupdf.open("pdf", pdf_bytes)
                    doc.delete_page(pdf_index)
                    page = doc.new_page(
                        pdf_index, width=pdf_rect.width, height=pdf_rect.height
                    )
                    page.show_pdf_page(pdf_rect, img_pdf, 0)
                    img_pdf.close()
                    del img_pdf
                    print(f"Image {pdf_index} added to PDF document.")
    doc.save(output_file)
    doc.close()

    end_time = time.time_ns()
    print(
        f"PDF file saved to {output_file} in {(end_time - start_time) / 1e9:.2f} seconds."
    )
    # del image_list
    gc.collect()


# ----------------------------------Below are the window and widgets configuration codes--------------------------------
FUNC_DISPLAY_NAME = "Images to PDF"
PARAM_GROUP_MAIN = "Main"

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

# --------------------------------Add the function to GUIAdapter instance------------------------------------------------


def use(adapter: GUIAdapter):
    adapter.add(
        images2pdf,
        cancelable=False,
        display_name=FUNC_DISPLAY_NAME,
        # document=FUNC_DOCUMENT,
        # document_format=FUNC_DOCUMENT_FORMAT,
        # icon=FUNC_ICON,
        # widget_configs=WIDGET_CONFIGS,
        window_config=EXEC_WINDOW_CONFIG,
    )
