"""
Calendar Router
"""

from fastapi import APIRouter, Depends, Query
from app.dependencies import get_current_user_id
from app.schemas.calendar import CalendarResponse
from app.services.calendar_service import calendar_service

router = APIRouter(prefix="/calendar", tags=["Calendar"])


@router.get("", response_model=CalendarResponse)
async def get_calendar(
    start: str = Query(..., examples=["2026-09-01"], description="Start date (YYYY-MM-DD)"),
    end: str = Query(..., examples=["2026-09-30"], description="End date (YYYY-MM-DD)"),
    user_id: str = Depends(get_current_user_id),
):
    """
    Unified calendar endpoint aggregating:
    - Todos
    - Classes (expanded occurrences)
    - Assignments
    - Exams
    - Hackathons
    - Certifications
    - Internships
    - Events
    across the specified date window.
    """
    return await calendar_service.get_calendar(user_id, start_date=start, end_date=end)
