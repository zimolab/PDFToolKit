from pathlib import Path
from typing import Literal, Union, Optional

import pymupdf.utils
import pymupdf
from pyguiadapter.adapter import uprogress, udialog
from pyguiadapter.adapter.ucontext import is_function_cancelled
from pyguiadapter.extend_types import file_t, directory_t
from pyguiadapter.widgets import (
    LineEditConfig,
    DirSelectConfig,
    FileSelectConfig,
    IntSpinBoxConfig,
    BoolBoxConfig,
    ExclusiveChoiceBoxConfig,
)
from pyguiadapter.windows.fnexec import FnExecuteWindowConfig, OutputBrowserConfig

from ..commons import GROUP_NAME
from ... import utils
from ...common_configs import parameters
from ...common_validators.basic import ensure_non_empty_string
from ...common_validators.filepath import ensure_file_exists
from ...common_variables import rand, runtime, dtime
from ...core.filename_generator import FilenameGenerator
from ...core.page_iterator import ALL_PAGES, PageIterator
from ...exceptions import DuplicateFileError
from ...rect_widget import rect_tuple_t, RectWidgetConfig

DEF_INPUT_FILE = ""

# variable "$indir" will be replaced with the input file's directory path in the run time, so,
# "$indir/output/" points to the an sub-directory named "output" of the input file's parent directory
DEF_OUTPUT_DIR = "$indir/output/"

# variable "$page" will be replaced with the current page number in the run time, so,
# "page-$page.png" generates filenames like "page-1.png", "page-2.png", etc.
DEF_FILENAME_PATTERN = "page-$page.png"

# by default, convert all pages in the document to image files
DEF_PAGE_RANGES = ALL_PAGES

# by default, use 96 DPI for image conversion
DEF_DPI = 96

DUPLICATE_FILE_POLICY_SKIP = "skip"
DUPLICATE_FILE_POLICY_OVERWRITE = "overwrite"
DUPLICATE_FILE_POLICY_ASK = "ask"
DUPLICATE_FILE_POLICY_FAIL = "fail"

# by default, overwrite existing files
DEF_DUPLICATE_FILE_POLICY = DUPLICATE_FILE_POLICY_OVERWRITE

# by default, verbose output is enabled
DEF_VERBOSE = True

# by default, do not crop the image with a cropbox
DEF_CROPBOX = None

# by default, do not add alpha channel to the image
DEF_ALPHA_CHANNEL = False

# by default, do not rotate the image
DEF_ROTATION = None

# by default, annotations on the page will be rendered
DEF_RENDER_ANNOTATIONS = True

CS_RGB = "RGB"
CS_GRAY = "GRAY"
CS_CMYK = "CMYK"

DEF_COLORSPACE = CS_RGB


def process_duplicate_file(
    filepath: Union[str, Path], policy: Literal["skip", "overwrite", "ask", "fail"]
) -> Optional[bool]:
    fp = Path(filepath)
    if not fp.is_file():
        return None

    # file already exists
    if policy == DUPLICATE_FILE_POLICY_SKIP:
        return False
    elif policy == DUPLICATE_FILE_POLICY_OVERWRITE:
        return True
    elif policy == DUPLICATE_FILE_POLICY_ASK:
        ret = udialog.show_question_messagebox(
            f"File {filepath} already exists. Do you want to overwrite it?",
            buttons=udialog.Yes | udialog.No,
        )
        return ret == udialog.Yes
    else:
        raise DuplicateFileError(f"duplicate file: {filepath}")


# Main function
def pdf2images(
    input_file: file_t = DEF_INPUT_FILE,
    output_dir: directory_t = DEF_OUTPUT_DIR,
    filename_pattern: str = DEF_FILENAME_PATTERN,
    page_ranges: str = DEF_PAGE_RANGES,
    dpi: int = DEF_DPI,
    cropbox: rect_tuple_t = DEF_CROPBOX,
    alpha_channel: bool = DEF_ALPHA_CHANNEL,
    rotation: int = DEF_ROTATION,
    render_annotations: bool = DEF_RENDER_ANNOTATIONS,
    colorspace: Literal["RGB", "GRAY", "CMYK"] = DEF_COLORSPACE,
    duplicate_file_policy: Literal[
        "skip", "overwrite", "ask", "fail"
    ] = DEF_DUPLICATE_FILE_POLICY,
    verbose: bool = DEF_VERBOSE,
):
    output_dir = output_dir or DEF_OUTPUT_DIR
    page_ranges = page_ranges or ALL_PAGES
    input_file_path = Path(input_file).absolute()

    ensure_file_exists("input_file", input_file)
    ensure_non_empty_string("filename_pattern", filename_pattern)

    document = None
    try:
        # open input file and get the document object of it
        document = pymupdf.open(input_file)

        # create page iterator for current document
        page_iterator = PageIterator(page_ranges, document)

        # create context with relevant variables
        context = {
            **runtime.VARIABLES,
            **dtime.VARIABLES,
            **rand.VARIABLES,
        }
        # create filename generator with the context
        filename_generator = FilenameGenerator(context)

        # update context variables
        # update relevant runtime variables
        # runtime.VARNAME_TOTAL set to total number of pages in current document
        filename_generator.update_context(runtime.VARNAME_TOTAL, document.page_count)
        # runtime.VARNAME_INPUT_FILENAME set to input file name
        filename_generator.update_context(
            runtime.VARNAME_INPUT_FILENAME, input_file_path.name
        )
        # runtime.VARNAME_INPUT_FILE_DIR set to input file directory
        filename_generator.update_context(
            runtime.VARNAME_INPUT_FILE_DIR, input_file_path.parent
        )
        # runtime.VARNAME_CWD_DIR set to current working directory
        filename_generator.update_context(runtime.VARNAME_CWD_DIR, utils.cwd())

        # output_dir also supports variable replacement
        output_dir = filename_generator.generate(output_dir)
        output_dir_path = Path(output_dir).absolute()
        if not output_dir_path.is_dir():
            output_dir_path.mkdir(parents=True, exist_ok=True)

        # show progressbar
        uprogress.show_progressbar(
            min_value=1, max_value=document.page_count, message_visible=False
        )

        for page_index in page_iterator.page_indexes():
            # handle cancellation
            if is_function_cancelled():
                break

            # update progress
            progress_info = f"converting page {page_index+1} of {document.page_count}"
            uprogress.update_progress(page_index + 1, info=progress_info)

            # update relevant variables per iteration
            filename_generator.update_context(runtime.VARNAME_CUR_INDEX, page_index)
            filename_generator.update_context(runtime.VARNAME_CUR_PAGE, page_index + 1)
            # generate output filename
            filename = filename_generator.generate(filename_pattern)
            # get output filepath and create parent directories if necessary
            output_filepath = output_dir_path.joinpath(filename)
            base_dir = output_filepath.parent
            if not base_dir.is_dir():
                base_dir.mkdir(parents=True, exist_ok=True)

            # convert page to image
            page = document[page_index]

            if cropbox is not None and cropbox != (0, 0, 0, 0):
                left, top, right, bottom = cropbox
                page.set_cropbox(pymupdf.Rect(left, top, right, bottom))

            if rotation is not None and rotation != 0:
                page.set_rotation(rotation)

            ret = process_duplicate_file(output_filepath, duplicate_file_policy)
            if ret is False:
                utils.pprint(
                    f"skipping {output_filepath} (duplicated file)", verbose=verbose
                )
                continue

            if ret is None:
                utils.pprint(f"creating {output_filepath}", verbose=verbose)

            if ret is True:
                utils.pprint(f"overwriting {output_filepath}", verbose=verbose)

            pixmap = page.get_pixmap(
                dpi=dpi,
                alpha=alpha_channel,
                annots=render_annotations,
                colorspace=colorspace,
            )
            # save image to output filepath
            pixmap.save(output_filepath)
            del page
            del pixmap
        filename_generator.clear_context()
    except Exception as e:
        raise e
    finally:
        # hide progressbar
        uprogress.hide_progressbar()
        if isinstance(document, pymupdf.Document):
            if not document.is_closed:
                document.close()
                del document
        # fitz.TOOLS.store_shrink(100)


CANCELABLE = True
GROUP = GROUP_NAME
ICON = "fa5.images"
DISPLAY_NAME = "PDF to Images"

PARAM_GROUP_MAIN = "Main Options"
PARAM_GROUP_IMAGE = "Image Options"
PARAM_GROUP_MISC = "Misc Options"

WIDGET_CONFIGS = {
    "input_file": FileSelectConfig(
        label="Input file",
        default_value=DEF_INPUT_FILE,
    ),
    "page_ranges": parameters.PAGE_RANGES,
    "filename_pattern": LineEditConfig(
        label="Filename pattern",
        default_value=DEF_FILENAME_PATTERN,
    ),
    "output_dir": DirSelectConfig(
        label="Output directory",
        default_value=DEF_OUTPUT_DIR,
    ),
    "dpi": IntSpinBoxConfig(
        label="DPI",
        default_value=DEF_DPI,
        min_value=1,
        max_value=5000,
        step=10,
        group=PARAM_GROUP_IMAGE,
    ),
    "cropbox": RectWidgetConfig(
        label="Crop Box",
        default_value=DEF_CROPBOX,
        default_value_description="No crop box",
        group=PARAM_GROUP_IMAGE,
        labels=("Left", "Top", "Right", "Bottom"),
    ),
    "alpha_channel": BoolBoxConfig(
        label="Alpha Channel",
        default_value=DEF_ALPHA_CHANNEL,
        true_text="Enabled",
        false_text="Disabled",
        group=PARAM_GROUP_IMAGE,
    ),
    "rotation": IntSpinBoxConfig(
        label="Rotation",
        default_value=DEF_ROTATION,
        default_value_description="No rotation",
        min_value=0,
        max_value=360,
        step=90,
        group=PARAM_GROUP_IMAGE,
    ),
    "render_annotations": BoolBoxConfig(
        label="Annotations",
        default_value=DEF_RENDER_ANNOTATIONS,
        true_text="Render",
        false_text="Suppress",
        group=PARAM_GROUP_IMAGE,
    ),
    "colorspace": ExclusiveChoiceBoxConfig(
        label="Colorspace",
        default_value=DEF_COLORSPACE,
        default_value_description="Auto",
        choices=[CS_RGB, CS_GRAY, CS_CMYK],
        group=PARAM_GROUP_IMAGE,
    ),
    "verbose": BoolBoxConfig(
        label="Verbose",
        default_value=DEF_VERBOSE,
        true_text="Enabled",
        false_text="Disabled",
        group=PARAM_GROUP_MISC,
    ),
    "duplicate_file_policy": ExclusiveChoiceBoxConfig(
        label="Duplicate File Policy",
        default_value=DEF_DUPLICATE_FILE_POLICY,
    ),
}
WINDOW_CONFIG = FnExecuteWindowConfig(
    title="PDF to Images",
    execute_button_text="Convert",
    output_browser_config=OutputBrowserConfig(font_size=16),
    print_function_result=False,
    print_function_error=False,
    default_parameter_group_name=PARAM_GROUP_MAIN,
)
