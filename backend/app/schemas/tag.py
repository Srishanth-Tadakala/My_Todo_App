"""
Tag Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    color: Optional[str] = Field(default="#6B7280", max_length=20)


class TagResponse(BaseModel):
    id: str
    user_id: str
    name: str
    color: Optional[str] = None
    created_at: Optional[str] = None
