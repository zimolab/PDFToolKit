from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pymupdf
from py_multitasking import TaskContext, TaskSession
from pyguiadapter.adapter.udialog import (
    show_warning_messagebox,
    show_question_messagebox,
)
from pyguiadapter.adapter.useful import highlight_parameter
from pyguiadapter.exceptions import ParameterError
from pyguiadapter.utils import Yes, No

from ..commons import check_cancel_event
from ..commons.context import runtime, dtime, rand
from ... import logme
from ...translation import t, app_t
from ...utils import close_safely, cwd

_DUPLICATE_POLICY_CONFIRM = 0
_DUPLICATE_POLICY_ON_OVERWRITE = 1
_DUPLICATE_POLICY_OVERWRITE = 2


def _this_t(key: str, prefix: str = "app.tools.images2pdf") -> str:
    return t(key, prefix)


_DUPLICATE_POLICIES = {
    _this_t("duplicate_confirm"): _DUPLICATE_POLICY_CONFIRM,
    _this_t("duplicate_no_overwrite"): _DUPLICATE_POLICY_ON_OVERWRITE,
    _this_t("duplicate_overwrite"): _DUPLICATE_POLICY_OVERWRITE,
}

_L = logme.new("pdftoolkit.tools.images2pdf")


@dataclass
class _ImageData(object):
    index: int | None = None
    data: bytes | None = None
    size: tuple[int, int] | None = None
    exception: Exception | None = None


def _process_page_images(ctx: TaskContext | None, image_items: list[tuple[int, str]]):
    for page_index, image_path in image_items:
        if check_cancel_event(ctx):
            _L.info("cancel event detected, stopping processing")
            break
        image_data = _produce_image_data(image_path, page_index)
        ctx.write_output(image_data, block=True)
    pymupdf.TOOLS.store_shrink(100)


def _blank_document(page_count: int) -> pymupdf.Document:
    doc = pymupdf.Document()
    for i in range(page_count):
        # this method exists but is not resolved by IDE, don't know why
        # noinspection PyUnresolvedReferences
        doc.insert_page(i)
    return doc


def _replace_page(doc: pymupdf.Document, image_data: _ImageData):
    page_doc = None
    page_index = image_data.index
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


def _produce_image_data(image_path: str, page_index: int) -> _ImageData:
    img_doc = None
    try:
        img_doc = pymupdf.open(image_path)
        raw: pymupdf.Rect = img_doc[0].rect
        img_size = (raw.width, raw.height)
        img_data = img_doc.convert_to_pdf()
        return _ImageData(
            index=page_index, data=img_data, size=img_size, exception=None
        )
    except Exception as e:
        _L.error(f"error processing image {image_path}: {e}")
        return _ImageData(index=page_index, exception=e)
    finally:
        if img_doc:
            close_safely(img_doc)


def _process_duplicate_dest_file(dest_file_path: Path, duplicate_policy: int) -> bool:
    if not dest_file_path.is_file():
        return True

    if duplicate_policy == _DUPLICATE_POLICY_OVERWRITE:
        return True

    if duplicate_policy == _DUPLICATE_POLICY_ON_OVERWRITE:
        show_warning_messagebox(
            text=_this_t("overwrite_not_allowed_msg"), title=app_t("warning_dlg_title")
        )
        highlight_parameter("dest_file")
        return False

    if duplicate_policy == _DUPLICATE_POLICY_CONFIRM:
        ret = show_question_messagebox(
            text=_this_t("overwrite_confirm_msg"),
            title=app_t("confirm_dlg_title"),
            buttons=Yes | No,
            default_button=Yes,
        )
        if ret != Yes:
            show_warning_messagebox(
                text=_this_t("overwrite_not_allowed_msg"),
                title=app_t("warning_dlg_title"),
            )
            highlight_parameter("dest_file")
            return False
        return True

    raise ParameterError(
        "duplicate_policy", "invalid duplicate policy value: {duplicate_policy}"
    )


def _build_name_context(image_count: int) -> dict[str, Any]:
    return {
        **runtime.VARIABLES,
        **dtime.VARIABLES,
        **rand.VARIABLES,
        runtime.VARNAME_TOTAL: image_count,
        runtime.VARNAME_CWD_DIR: cwd(),
    }


def _cleanup_session(session: TaskSession):
    session.cancel_all(with_cancel_event_set=True)
    session.wait_for_all()
    _ = session.context.read_output_until_empty()
    session.destroy()
    pymupdf.TOOLS.store_shrink(100)
