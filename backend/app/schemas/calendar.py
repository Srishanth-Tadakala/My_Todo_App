"""
Unified Calendar Schemas
"""

from typing import Any, Dict, List
from pydantic import BaseModel, Field


class CalendarResponse(BaseModel):
    todos: List[Dict[str, Any]] = Field(default_factory=list)
    classes: List[Dict[str, Any]] = Field(default_factory=list)
    assignments: List[Dict[str, Any]] = Field(default_factory=list)
    exams: List[Dict[str, Any]] = Field(default_factory=list)
    hackathons: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[Dict[str, Any]] = Field(default_factory=list)
    internships: List[Dict[str, Any]] = Field(default_factory=list)
    events: List[Dict[str, Any]] = Field(default_factory=list)
