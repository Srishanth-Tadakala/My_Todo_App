"""
Exam Schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field, model_validator
from app.utils.datetime import parse_time


class ExamCreate(BaseModel):
    subject_id: Optional[str] = None
    title: str = Field(min_length=1, max_length=150)
    exam_date: str  # YYYY-MM-DD
    start_time: str  # HH:MM:SS
    end_time: str    # HH:MM:SS
    building: Optional[str] = Field(default=None, max_length=100)
    floor: Optional[str] = Field(default=None, max_length=50)
    room: Optional[str] = Field(default=None, max_length=50)
    syllabus: Optional[str] = Field(default=None, max_length=2000)
    notes: Optional[str] = Field(default=None, max_length=1000)
    reminder_offsets: Optional[List[int]] = Field(default=[10080, 1440, 120])  # 7d, 1d, 2h in minutes

    @model_validator(mode="after")
    def validate_times(self):
        st = parse_time(self.start_time)
        et = parse_time(self.end_time)
        if et <= st:
            raise ValueError("end_time must be strictly after start_time")
        return self


class ExamUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    exam_date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    syllabus: Optional[str] = None
    notes: Optional[str] = None
    reminder_offsets: Optional[List[int]] = None


class ExamResponse(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str] = None
    title: str
    exam_date: str
    start_time: str
    end_time: str
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    syllabus: Optional[str] = None
    notes: Optional[str] = None
    reminder_offsets: List[int] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
