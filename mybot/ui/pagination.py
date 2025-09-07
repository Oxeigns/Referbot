"""Pagination helpers."""
from __future__ import annotations

from math import ceil
from typing import Iterable, List, Tuple, TypeVar

T = TypeVar("T")


def paginate(items: Iterable[T], page: int, page_size: int) -> Tuple[List[T], int]:
    """Return slice of items for page and total pages."""
    items_list = list(items)
    total_pages = max(1, ceil(len(items_list) / page_size))
    page = max(1, min(page, total_pages))
    start = (page - 1) * page_size
    end = start + page_size
    return items_list[start:end], total_pages


def page_directions(page: int, total_pages: int) -> Tuple[int | None, int | None]:
    """Return previous and next page numbers if available."""
    prev_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None
    return prev_page, next_page
