"""
User Profile and Settings Schemas
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, max_length=100)
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    timezone: Optional[str] = Field(default=None, max_length=50)


class ProfileResponse(BaseModel):
    id: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class UserSettingsUpdate(BaseModel):
    default_reminder_minutes: Optional[int] = Field(default=None, ge=0, le=10080)
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None  # HH:MM:SS
    quiet_hours_end: Optional[str] = None    # HH:MM:SS
    timezone: Optional[str] = None
    daily_summary_enabled: Optional[bool] = None
    daily_summary_time: Optional[str] = None
    weekly_summary_enabled: Optional[bool] = None
    sound_enabled: Optional[bool] = None
    vibration_enabled: Optional[bool] = None


class UserSettingsResponse(BaseModel):
    user_id: str
    default_reminder_minutes: int
    quiet_hours_enabled: bool
    quiet_hours_start: str
    quiet_hours_end: str
    timezone: str
    daily_summary_enabled: bool
    daily_summary_time: str
    weekly_summary_enabled: bool
    sound_enabled: bool
    vibration_enabled: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
