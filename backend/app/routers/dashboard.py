"""
Dashboard Router
"""

from fastapi import APIRouter, Depends
from app.dependencies import get_current_user_id
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import dashboard_service

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(user_id: str = Depends(get_current_user_id)):
    """
    Returns single aggregated payload for the Expo mobile app home screen:
    - Today's completion & overdue metrics
    - Next upcoming class/schedule item
    - Today's full schedule
    - Upcoming deadlines across all entities for the next 7 days
    - Overdue tasks needing immediate attention
    """
    return await dashboard_service.get_dashboard(user_id)
