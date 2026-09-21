"""
Reminder Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    TODO = "TODO"
    SCHEDULE = "SCHEDULE"
    ASSIGNMENT = "ASSIGNMENT"
    EXAM = "EXAM"
    HACKATHON = "HACKATHON"
    CERTIFICATION = "CERTIFICATION"
    INTERNSHIP = "INTERNSHIP"
    EVENT = "EVENT"


class ChannelType(str, Enum):
    PUSH = "PUSH"
    IN_APP = "IN_APP"


class ReminderStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SENT = "SENT"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ReminderType(str, Enum):
    DUE_SOON = "DUE_SOON"
    DUE_NOW = "DUE_NOW"
    OVERDUE = "OVERDUE"
    CLASS_STARTING = "CLASS_STARTING"
    DEADLINE_APPROACHING = "DEADLINE_APPROACHING"
    CERTIFICATION_EXPIRING = "CERTIFICATION_EXPIRING"
    INTERVIEW_UPCOMING = "INTERVIEW_UPCOMING"
    EVENT_STARTING = "EVENT_STARTING"


class ReminderCreate(BaseModel):
    entity_type: EntityType
    entity_id: str
    reminder_type: Optional[ReminderType] = ReminderType.DUE_SOON
    remind_at: str
    channel: Optional[ChannelType] = ChannelType.PUSH


class ReminderUpdate(BaseModel):
    remind_at: Optional[str] = None
    channel: Optional[ChannelType] = None
    status: Optional[ReminderStatus] = None


class ReminderResponse(BaseModel):
    id: str
    user_id: str
    entity_type: str
    entity_id: str
    reminder_type: str
    remind_at: str
    channel: str
    status: str
    attempt_count: int = 0
    last_attempt_at: Optional[str] = None
    next_retry_at: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
