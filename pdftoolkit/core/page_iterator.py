from typing import Generator

from pymupdf import Document, Page

ODD_PAGES = "ODD"
EVEN_PAGES = "EVEN"
ALL_PAGES = "ALL"
LAST_PAGE = "N"

SPECIAL_PAGE_RANGES = (ODD_PAGES, EVEN_PAGES, ALL_PAGES, LAST_PAGE)

class InvalidPageRangeError(Exception):
    pass

class PageIterator(object):
    """Page iterator for a page range string like 1-3,5,7-9 """

    def __init__(self, page_ranges: str, doc: Document):
        # assert isinstance(page_ranges, str)
        # assert isinstance(doc, Document)

        self._page_ranges = self._normalize_page_ranges_str(page_ranges)
        self._doc = doc

    def __iter__(self):
        return self.page_indexes()

    def page_indexes(self):
        index_sections = self._page_index_sections(self._page_ranges, self._doc.page_count)
        for indexes in index_sections:
            if isinstance(indexes, (range, list)):
                for idx in indexes:
                    yield idx
            else:
                yield indexes

    def pages(self):
        for index in self.page_indexes():
            page: Page = self._doc[index]
            yield page

    @staticmethod
    def _normalize_page_ranges_str(page_ranges: str):
        page_ranges = page_ranges.strip().upper().replace(" ", "").replace("，", ",")
        if not page_ranges:
            return ALL_PAGES
        return page_ranges

    def _page_index_sections(self, page_ranges: str, page_count: int) -> list[range | int]:
        section_strs = [range_str.strip() for range_str in page_ranges.split(",") if range_str.strip() != ""]
        sections: list[range| list[int] | int] = []
        for section_str in section_strs:
            section_str = section_str.upper()

            # for odd pages
            if section_str == ODD_PAGES:
                sections.append(range(1, page_count, 2))
                continue

            # for even pages
            if section_str == EVEN_PAGES:
                sections.append(range(0, page_count, 2))
                continue

            # for all pages
            if section_str == ALL_PAGES:
                sections.append(range(0, page_count))
                continue

            # single page number, like 5, 10 or N
            if section_str.isdigit() or section_str == LAST_PAGE:
                sections.append(self._to_page_index(section_str, page_count))
                continue

            # page range, like 1-3, 5-7, 9-10
            if "-" in section_str:
                sections.append(self._to_page_index_range(section_str, page_count))
                continue

            # invalid page range
            raise InvalidPageRangeError(f"Invalid page range: {section_str}")

        return sections


    def _to_page_index_range(self, range_str: str, page_count: int) -> range | list[int]:
        tmp  = [num.strip() for num in range_str.split("-") if num.strip() != ""]
        if len(tmp) != 2:
            raise InvalidPageRangeError(f"Invalid page range: {range_str}")
        start, end = tmp
        try:
            start_index = self._to_page_index(start, page_count)
            end_index = self._to_page_index(end, page_count)
        except InvalidPageRangeError as e:
            raise InvalidPageRangeError(f"Invalid page range: {range_str}") from e
        if start_index <= end_index + 1:
            return range(start_index, end_index + 1)
        # if start_index > end_index, it means the range is reversed, like 10-1, 10-2, 10-3
        indexes = [idx for idx in range(end_index, start_index + 1)]
        indexes.reverse()
        return indexes

    @staticmethod
    def _to_page_index(page_num_str: str, page_count: int) -> int:
        if page_num_str == LAST_PAGE:
            return page_count - 1
        try:
            page_num = int(page_num_str)
        except ValueError as e:
            raise InvalidPageRangeError(f"Invalid page number: {page_num_str}") from e
        else:
            if page_num < 1 or page_num > page_count:
                raise InvalidPageRangeError(f"Invalid page number: {page_num_str}")
            return page_num - 1
