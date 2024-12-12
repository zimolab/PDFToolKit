from dataclasses import dataclass

import pymupdf
from py_multitasking import TaskContext

from ..commons import check_cancel_event
from ... import logme
from ...translation import t
from ...utils import close_safely


ERROR_POLICY_STOP = 0
ERROR_POLICY_CONTINUE = 1

DUPLICATE_POLICY_ON_OVERWRITE = 0
DUPLICATE_POLICY_CONFIRM = 1
DUPLICATE_POLICY_OVERWRITE = 2

DUPLICATE_POLICIES = {
    DUPLICATE_POLICY_ON_OVERWRITE,
    DUPLICATE_POLICY_CONFIRM,
    DUPLICATE_POLICY_OVERWRITE,
}

_L = logme.new("pdftoolkit.tools.images2pdf")


def _this_t(key: str, prefix: str = "app.tools.images2pdf") -> str:
    return t(key, prefix)


@dataclass
class ImageData(object):
    index: int | None = None
    data: bytes | None = None
    size: tuple[int, int] | None = None
    exception: Exception | None = None


def produce_image_data(image_path: str, page_index: int) -> ImageData:
    img_doc = None
    try:
        img_doc = pymupdf.open(image_path)
        raw: pymupdf.Rect = img_doc[0].rect
        img_size = (raw.width, raw.height)
        img_data = img_doc.convert_to_pdf()
        return ImageData(index=page_index, data=img_data, size=img_size, exception=None)
    except Exception as e:
        _L.error(f"error processing image {image_path}: {e}")
        return ImageData(index=page_index, exception=e)
    finally:
        if img_doc:
            close_safely(img_doc)


def process_page_images(
    ctx: TaskContext | None, images: list[tuple[int, str]], error_policy: int
):
    assert ctx is not None
    assert ctx.has_output_queue()
    assert error_policy in (ERROR_POLICY_STOP, ERROR_POLICY_CONTINUE)

    for page_index, image_path in images:
        if check_cancel_event(ctx):
            _L.info("cancel event detected, stopping processing")
            break

        image_data = produce_image_data(image_path, page_index)
        ctx.write_output(image_data, block=True)

        if image_data.exception and error_policy == ERROR_POLICY_STOP:
            _L.error(
                f"an error occurred while processing image {image_path}, error_policy is set to stop, stopping processing"
            )
            break


def blank_document(page_count: int) -> pymupdf.Document:
    doc = pymupdf.Document()
    for i in range(page_count):
        # this method exists but is not resolved by IDE, don't know why
        # noinspection PyUnresolvedReferences
        doc.insert_page(i)
    return doc


def replace_page(doc: pymupdf.Document, page_index: int, image_data: ImageData):
    page_doc = None
    try:
        page_doc = pymupdf.open("pdf", image_data.data)
        doc.delete_page(page_index)
        # this method exists but is not resolved by IDE, don't know why
        # noinspection PyUnresolvedReferences
        new_page: pymupdf.Page = doc.new_page(
            page_index, width=image_data.size[0], height=image_data.size[1]
        )
        new_page_rect = pymupdf.Rect(0, 0, image_data.size[0], image_data.size[1])
        # this method exists but is not resolved by IDE, don't know why
        # noinspection PyUnresolvedReferences
        new_page.show_pdf_page(new_page_rect, page_doc)
    except Exception as e:
        _L.error(f"error replacing page {page_index} with image data: {e}")
        raise e
    finally:
        if page_doc:
            close_safely(page_doc)
