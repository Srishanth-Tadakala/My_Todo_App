"""
Personal Events Schemas
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, model_validator
from app.utils.datetime import parse_datetime


class EventCreate(BaseModel):
    title: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=2000)
    start_at: str
    end_at: str
    location: Optional[str] = Field(default=None, max_length=150)
    reminder_enabled: Optional[bool] = True
    reminder_minutes: Optional[int] = Field(default=30, ge=0)
    repeat_rule: Optional[Dict[str, Any]] = None

    @model_validator(mode="after")
    def validate_times(self):
        s = parse_datetime(self.start_at)
        e = parse_datetime(self.end_at)
        if e <= s:
            raise ValueError("end_at must be after start_at")
        return self


class EventUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    start_at: Optional[str] = None
    end_at: Optional[str] = None
    location: Optional[str] = None
    reminder_enabled: Optional[bool] = None
    reminder_minutes: Optional[int] = Field(default=None, ge=0)
    repeat_rule: Optional[Dict[str, Any]] = None


class EventResponse(BaseModel):
    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    start_at: str
    end_at: str
    location: Optional[str] = None
    reminder_enabled: bool
    reminder_minutes: int
    repeat_rule: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
