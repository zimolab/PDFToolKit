from pathlib import Path

from pyguiadapter.adapter.udialog import (
    show_question_messagebox,
    show_warning_messagebox,
)
from pyguiadapter.adapter.useful import highlight_parameter
from pyguiadapter.exceptions import ParameterError
from pyguiadapter.extend_types import file_list_t, file_t
from pyguiadapter.utils import Yes, No

from ._commons import (
    DUPLICATE_POLICY_CONFIRM,
    DUPLICATE_POLICIES,
    DUPLICATE_POLICY_OVERWRITE,
    DUPLICATE_POLICY_ON_OVERWRITE,
    _this_t,
)
from ..commons.validators import ensure_non_empty_sequence, ensure_in_set
from ...translation import app_t


def _process_duplicate_dest_file(dest_file_path: Path, duplicate_policy: int) -> bool:
    if not dest_file_path.is_file():
        return True

    if duplicate_policy == DUPLICATE_POLICY_OVERWRITE:
        return True

    if duplicate_policy == DUPLICATE_POLICY_ON_OVERWRITE:
        show_warning_messagebox(
            text=_this_t("overwrite_not_allowed_msg"), title=app_t("warning_dlg_title")
        )
        highlight_parameter("dest_file")
        return False

    if duplicate_policy == DUPLICATE_POLICY_CONFIRM:
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


def files2pdf(
    image_files: file_list_t,
    dest_file: file_t,
    duplicate_policy: int = DUPLICATE_POLICY_CONFIRM,
    worker_count: int = 1,
):
    ensure_non_empty_sequence("image_files", image_files)
    ensure_in_set("duplicate_policy", duplicate_policy, DUPLICATE_POLICIES)

    dest_file_path = Path(dest_file)
    if not _process_duplicate_dest_file(dest_file_path, duplicate_policy):
        return
