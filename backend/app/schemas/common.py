"""
Common Pydantic Schemas
"""

from typing import Any, Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    total: int = Field(default=0, ge=0)
    total_pages: int = Field(default=1, ge=1)


class ConflictItem(BaseModel):
    conflicting_item_id: str
    conflicting_title: str
    start_time: str
    end_time: str
    message: str


class ConflictCheckResult(BaseModel):
    has_conflict: bool
    conflicts: List[ConflictItem] = []
