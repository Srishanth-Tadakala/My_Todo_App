"""
Notification and Device Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class DeviceRegisterRequest(BaseModel):
    expo_push_token: str = Field(min_length=10, max_length=200)
    platform: str = Field(default="android", pattern="^(ios|android|web)$")
    device_name: Optional[str] = Field(default=None, max_length=100)


class DeviceResponse(BaseModel):
    id: str
    user_id: str
    expo_push_token: str
    platform: str
    device_name: Optional[str] = None
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class NotificationLogResponse(BaseModel):
    id: str
    user_id: str
    entity_type: str
    entity_id: str
    reminder_id: Optional[str] = None
    notification_type: str
    title: str
    body: str
    channel: str
    sent_at: str
    status: str
    error_message: Optional[str] = None
    created_at: Optional[str] = None
