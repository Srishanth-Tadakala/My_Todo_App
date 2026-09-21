"""
Analytics Router
"""

from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user_id
from app.schemas.analytics import AnalyticsSummaryResponse
from app.services.analytics_service import analytics_service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    period: str = Query("today", pattern="^(today|this_week|this_month)$"),
    user_id: str = Depends(get_current_user_id),
):
    """Returns productivity statistics (created, completed, pending, overdue, postponed, completion rate)."""
    return await analytics_service.get_summary(user_id, period)
