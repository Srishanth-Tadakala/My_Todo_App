"""
Productivity Analytics Schemas
"""

from typing import Optional
from pydantic import BaseModel


class AnalyticsSummaryResponse(BaseModel):
    period: str  # today, this_week, this_month
    tasks_created: int = 0
    tasks_completed: int = 0
    tasks_pending: int = 0
    tasks_overdue: int = 0
    tasks_postponed: int = 0
    completion_rate: float = 0.0
