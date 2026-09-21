"""
Unified Search Schemas
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    type: str  # TODO, SUBJECT, ASSIGNMENT, EXAM, HACKATHON, CERTIFICATION, INTERNSHIP, PROJECT, EVENT
    id: str
    title: str
    description: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    total_results: int = 0
    results: List[SearchResultItem] = Field(default_factory=list)
