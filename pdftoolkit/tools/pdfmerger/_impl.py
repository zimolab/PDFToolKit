import time
from pathlib import Path

import pymupdf
from pyguiadapter.exceptions import ParameterError
from pyguiadapter.extend_types import file_list_t, file_t

from ...utils import pprint


def pdfmerger(pdf_files: file_list_t, output_file: file_t = "merged.pdf"):
    if not pdf_files:
        raise ParameterError("pdf_files", "No PDF files provided")

    if not output_file:
        raise ParameterError("output_file", "No output file provided")

    start_time = time.time_ns()

    merged_pdf = pymupdf.open()

    for pdf_file in pdf_files:
        input_pdf = pymupdf.open(pdf_file)
        merged_pdf.insert_pdf(input_pdf, 0, 200, show_progress=True)
        input_pdf.close()
    merged_pdf.save(output_file)
    merged_pdf.close()
    pprint(
        f"Merged PDF saved to: {Path(output_file).absolute().as_posix()}", verbose=True
    )
    pprint(f"Time elapsed: {(time.time_ns() - start_time)/1e9} seconds", verbose=True)
