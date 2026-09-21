"""
Timetable, Schedule Item, and Exception Schemas
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, model_validator
from app.utils.datetime import parse_time


class ScheduleType(str, Enum):
    CLASS = "CLASS"
    STUDY = "STUDY"
    PROJECT = "PROJECT"
    WORK = "WORK"
    MEETING = "MEETING"
    FITNESS = "FITNESS"
    PERSONAL = "PERSONAL"
    BREAK = "BREAK"
    OTHER = "OTHER"


class ExceptionType(str, Enum):
    CANCELLED = "CANCELLED"
    RESCHEDULED = "RESCHEDULED"
    LOCATION_CHANGED = "LOCATION_CHANGED"
    TIME_CHANGED = "TIME_CHANGED"


class TimetableCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    academic_year: Optional[str] = Field(default=None, max_length=20)
    semester: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = True


class TimetableUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    academic_year: Optional[str] = Field(default=None, max_length=20)
    semester: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None


class TimetableResponse(BaseModel):
    id: str
    user_id: str
    name: str
    academic_year: Optional[str] = None
    semester: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ScheduleItemCreate(BaseModel):
    timetable_id: str
    subject_id: Optional[str] = None
    title: str = Field(min_length=1, max_length=150)
    type: Optional[ScheduleType] = ScheduleType.CLASS
    day_of_week: int = Field(ge=0, le=6)  # 0=Monday, 6=Sunday
    start_time: str  # HH:MM:SS
    end_time: str    # HH:MM:SS
    repeat_rule: Optional[Dict[str, Any]] = None
    building: Optional[str] = Field(default=None, max_length=100)
    floor: Optional[str] = Field(default=None, max_length=50)
    room: Optional[str] = Field(default=None, max_length=50)
    teacher: Optional[str] = Field(default=None, max_length=100)
    reminder_enabled: Optional[bool] = True
    reminder_minutes: Optional[int] = Field(default=15, ge=0)
    notes: Optional[str] = Field(default=None, max_length=1000)

    @model_validator(mode="after")
    def validate_times(self):
        st = parse_time(self.start_time)
        et = parse_time(self.end_time)
        if et <= st:
            raise ValueError("end_time must be strictly after start_time")
        return self


class ScheduleItemUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    type: Optional[ScheduleType] = None
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    repeat_rule: Optional[Dict[str, Any]] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    teacher: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    reminder_minutes: Optional[int] = Field(default=None, ge=0)
    notes: Optional[str] = None


class ScheduleItemResponse(BaseModel):
    id: str
    user_id: str
    timetable_id: str
    subject_id: Optional[str] = None
    title: str
    type: str
    day_of_week: int
    start_time: str
    end_time: str
    repeat_rule: Optional[Dict[str, Any]] = None
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    teacher: Optional[str] = None
    reminder_enabled: bool
    reminder_minutes: int
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ScheduleExceptionCreate(BaseModel):
    schedule_item_id: str
    date: str  # YYYY-MM-DD
    exception_type: ExceptionType
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None
    new_building: Optional[str] = None
    new_floor: Optional[str] = None
    new_room: Optional[str] = None
    notes: Optional[str] = None


class ScheduleExceptionResponse(BaseModel):
    id: str
    schedule_item_id: str
    user_id: str
    date: str
    exception_type: str
    new_start_time: Optional[str] = None
    new_end_time: Optional[str] = None
    new_building: Optional[str] = None
    new_floor: Optional[str] = None
    new_room: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None


class ScheduleOccurrenceResponse(BaseModel):
    id: str
    schedule_item_id: str
    timetable_id: Optional[str] = None
    subject_id: Optional[str] = None
    title: str
    type: str
    date: str
    start_time: str
    end_time: str
    building: Optional[str] = None
    floor: Optional[str] = None
    room: Optional[str] = None
    teacher: Optional[str] = None
    is_exception: bool = False
    exception_type: Optional[str] = None
    notes: Optional[str] = None
