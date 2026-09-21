"""
Academic Subject Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, max_length=20)
    teacher: Optional[str] = Field(default=None, max_length=100)
    semester: Optional[str] = Field(default=None, max_length=50)
    academic_year: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default="#6366F1", max_length=20)
    notes: Optional[str] = Field(default=None, max_length=1000)


class SubjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, max_length=20)
    teacher: Optional[str] = Field(default=None, max_length=100)
    semester: Optional[str] = Field(default=None, max_length=50)
    academic_year: Optional[str] = Field(default=None, max_length=20)
    color: Optional[str] = Field(default=None, max_length=20)
    notes: Optional[str] = Field(default=None, max_length=1000)


class SubjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    code: Optional[str] = None
    teacher: Optional[str] = None
    semester: Optional[str] = None
    academic_year: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
