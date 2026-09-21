"""
Assignment Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl


class AssignmentStatus(str, Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    SUBMITTED = "SUBMITTED"
    COMPLETED = "COMPLETED"


class AssignmentPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class AssignmentCreate(BaseModel):
    subject_id: Optional[str] = None
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    assigned_at: Optional[str] = None
    due_at: str
    priority: Optional[AssignmentPriority] = AssignmentPriority.MEDIUM
    status: Optional[AssignmentStatus] = AssignmentStatus.NOT_STARTED
    submission_url: Optional[str] = Field(default=None, max_length=500)
    notes: Optional[str] = Field(default=None, max_length=1000)


class AssignmentUpdate(BaseModel):
    subject_id: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    assigned_at: Optional[str] = None
    due_at: Optional[str] = None
    priority: Optional[AssignmentPriority] = None
    status: Optional[AssignmentStatus] = None
    submission_url: Optional[str] = None
    notes: Optional[str] = None


class AssignmentResponse(BaseModel):
    id: str
    user_id: str
    subject_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    assigned_at: Optional[str] = None
    due_at: str
    priority: str
    status: str
    submission_url: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
