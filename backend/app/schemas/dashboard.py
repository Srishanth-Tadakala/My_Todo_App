"""
Dashboard API Schemas
Single payload for the Expo home screen.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class DashboardTodayStats(BaseModel):
    completed: int = 0
    pending: int = 0
    overdue: int = 0


class DeadlineItem(BaseModel):
    id: str
    entity_type: str  # TODO, ASSIGNMENT, EXAM, HACKATHON, CERTIFICATION
    title: str
    due_at: str
    priority: Optional[str] = None
    status: Optional[str] = None


class DashboardResponse(BaseModel):
    today: DashboardTodayStats = Field(default_factory=DashboardTodayStats)
    next_schedule: Optional[Dict[str, Any]] = None
    upcoming_deadlines: List[DeadlineItem] = Field(default_factory=list)
    overdue_tasks: List[Dict[str, Any]] = Field(default_factory=list)
    today_schedule: List[Dict[str, Any]] = Field(default_factory=list)
