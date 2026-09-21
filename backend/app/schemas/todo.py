"""
Todo and Subtask Schemas
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from app.schemas.tag import TagResponse


class TodoStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class TodoPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


# Subtask Schemas
class SubtaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    sort_order: Optional[int] = Field(default=0, ge=0)


class SubtaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    is_completed: Optional[bool] = None
    sort_order: Optional[int] = Field(default=None, ge=0)


class SubtaskResponse(BaseModel):
    id: str
    todo_id: str
    user_id: str
    title: str
    is_completed: bool
    completed_at: Optional[str] = None
    sort_order: int
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Todo Schemas
class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    list_id: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[TodoStatus] = TodoStatus.TODO
    priority: Optional[TodoPriority] = TodoPriority.MEDIUM
    due_at: Optional[str] = None
    timezone: Optional[str] = "UTC"
    estimated_minutes: Optional[int] = Field(default=None, ge=0)
    reminder_enabled: Optional[bool] = False
    reminder_minutes_before: Optional[int] = Field(default=30, ge=0)
    tag_ids: Optional[List[str]] = Field(default_factory=list)


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    list_id: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[TodoStatus] = None
    priority: Optional[TodoPriority] = None
    due_at: Optional[str] = None
    timezone: Optional[str] = None
    estimated_minutes: Optional[int] = Field(default=None, ge=0)
    actual_minutes: Optional[int] = Field(default=None, ge=0)
    reminder_enabled: Optional[bool] = None
    tag_ids: Optional[List[str]] = None


class TodoReschedule(BaseModel):
    new_due_at: str
    reason: Optional[str] = None


class TodoPostpone(BaseModel):
    minutes: int = Field(default=1440, ge=1)
    reason: Optional[str] = None


class SubtaskProgress(BaseModel):
    total: int = 0
    completed: int = 0
    percentage: float = 0.0


class TodoResponse(BaseModel):
    id: str
    user_id: str
    list_id: Optional[str] = None
    project_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    priority: str
    due_at: Optional[str] = None
    timezone: str = "UTC"
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    reminder_enabled: bool = False
    completed_at: Optional[str] = None
    postponed_count: int = 0
    is_overdue: bool = False
    needs_reschedule_prompt: bool = False
    subtask_progress: SubtaskProgress = Field(default_factory=SubtaskProgress)
    subtasks: List[SubtaskResponse] = Field(default_factory=list)
    tags: List[TagResponse] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
