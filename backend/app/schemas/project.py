"""
Project Schemas
"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    PLANNING = "PLANNING"
    ACTIVE = "ACTIVE"
    ON_HOLD = "ON_HOLD"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[ProjectStatus] = ProjectStatus.PLANNING
    start_date: Optional[str] = None  # YYYY-MM-DD
    target_date: Optional[str] = None # YYYY-MM-DD


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=150)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    start_date: Optional[str] = None
    target_date: Optional[str] = None


class ProjectStats(BaseModel):
    total_tasks: int = 0
    completed_tasks: int = 0
    pending_tasks: int = 0
    completion_percentage: float = 0.0


class ProjectResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    status: str
    start_date: Optional[str] = None
    target_date: Optional[str] = None
    stats: Optional[ProjectStats] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
