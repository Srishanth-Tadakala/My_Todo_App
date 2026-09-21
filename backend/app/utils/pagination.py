"""
Pagination Helper Utilities
"""

import math
from typing import Any, Dict, List, TypeVar

T = TypeVar("T")


def build_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    page_size: int,
) -> Dict[str, Any]:
    """Formats items into a standard pagination dictionary."""
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    return {
        "items": items,
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, total_pages),
    }
