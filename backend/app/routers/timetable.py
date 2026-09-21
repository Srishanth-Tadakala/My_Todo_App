"""
Timetable and Schedule Items Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.common import ConflictCheckResult
from app.schemas.timetable import (
    ScheduleExceptionCreate, ScheduleExceptionResponse,
    ScheduleItemCreate, ScheduleItemResponse, ScheduleItemUpdate,
    ScheduleOccurrenceResponse, TimetableCreate, TimetableResponse, TimetableUpdate
)
from app.services.timetable_service import timetable_service

router = APIRouter(prefix="/timetable", tags=["Timetable"])


# 1. Base Timetables Listing & Creation
@router.get("", response_model=List[TimetableResponse])
async def list_timetables(user_id: str = Depends(get_current_user_id)):
    """Lists all timetables for the user."""
    return await timetable_service.list_timetables(user_id)


@router.post("", response_model=TimetableResponse, status_code=201)
async def create_timetable(req: TimetableCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new timetable."""
    return await timetable_service.create_timetable(user_id, req)


@router.get("/active", response_model=Optional[TimetableResponse])
async def get_active_timetable(user_id: str = Depends(get_current_user_id)):
    """Retrieves the currently active timetable."""
    return await timetable_service.get_active_timetable(user_id)


# 2. Conflict Detection
@router.get("/conflicts/check", response_model=ConflictCheckResult)
async def check_conflicts(
    timetable_id: str = Query(...),
    day_of_week: int = Query(..., ge=0, le=6),
    start_time: str = Query(..., examples=["09:00:00"]),
    end_time: str = Query(..., examples=["10:00:00"]),
    exclude_item_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    """
    Checks for schedule overlaps: existing.start < new.end AND existing.end > new.start.
    Returns conflicts to client without automatically rejecting.
    """
    return await timetable_service.detect_conflicts(
        user_id=user_id,
        timetable_id=timetable_id,
        day_of_week=day_of_week,
        start_time_str=start_time,
        end_time_str=end_time,
        exclude_item_id=exclude_item_id,
    )


# 3. Schedule Items
@router.get("/items", response_model=List[ScheduleItemResponse])
async def list_schedule_items(
    timetable_id: Optional[str] = Query(None),
    day_of_week: Optional[int] = Query(None, ge=0, le=6),
    user_id: str = Depends(get_current_user_id),
):
    """Lists base schedule items."""
    return await timetable_service.list_schedule_items(user_id, timetable_id=timetable_id, day_of_week=day_of_week)


@router.post("/items", response_model=ScheduleItemResponse, status_code=201)
async def create_schedule_item(req: ScheduleItemCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a base recurring schedule item."""
    return await timetable_service.create_schedule_item(user_id, req)


@router.get("/items/{item_id}", response_model=ScheduleItemResponse)
async def get_schedule_item(item_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves schedule item by ID."""
    return await timetable_service.get_schedule_item(item_id, user_id)


@router.put("/items/{item_id}", response_model=ScheduleItemResponse)
async def update_schedule_item(item_id: str, req: ScheduleItemUpdate, user_id: str = Depends(get_current_user_id)):
    """Updates a schedule item."""
    return await timetable_service.update_schedule_item(item_id, user_id, req)


@router.delete("/items/{item_id}", status_code=200)
async def delete_schedule_item(item_id: str, user_id: str = Depends(get_current_user_id)):
    """Soft deletes a schedule item."""
    await timetable_service.delete_schedule_item(item_id, user_id)
    return success_response({"message": "Schedule item deleted successfully."})


# 4. Occurrences & Windows (Dynamic Recurrence Projection)
@router.get("/occurrences", response_model=List[ScheduleOccurrenceResponse])
async def get_schedule_occurrences(
    start_date: str = Query(..., examples=["2026-09-01"]),
    end_date: str = Query(..., examples=["2026-09-07"]),
    timetable_id: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id),
):
    """
    Expands recurring schedule items across the specified date window,
    applying any exceptions (CANCELLED, RESCHEDULED, LOCATION_CHANGED).
    """
    return await timetable_service.get_occurrences(
        user_id=user_id,
        start_date_str=start_date,
        end_date_str=end_date,
        timetable_id=timetable_id,
    )


# 5. Schedule Exceptions
@router.post("/exceptions", response_model=ScheduleExceptionResponse, status_code=201)
async def create_exception(req: ScheduleExceptionCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a date-specific schedule exception for a single class occurrence."""
    return await timetable_service.create_exception(user_id, req)


@router.get("/items/{item_id}/exceptions", response_model=List[ScheduleExceptionResponse])
async def list_exceptions_for_item(item_id: str, user_id: str = Depends(get_current_user_id)):
    """Lists exceptions for a specific schedule item."""
    return await timetable_service.list_exceptions_for_item(item_id, user_id)


@router.delete("/exceptions/{exception_id}", status_code=200)
async def delete_exception(exception_id: str, user_id: str = Depends(get_current_user_id)):
    """Removes a schedule exception, restoring the base schedule item."""
    await timetable_service.delete_exception(exception_id, user_id)
    return success_response({"message": "Exception removed successfully."})


# 6. Parameterized Timetable ID routes (placed last so static paths take precedence)
@router.get("/{timetable_id}", response_model=TimetableResponse)
async def get_timetable(timetable_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves timetable by ID."""
    return await timetable_service.get_timetable(timetable_id, user_id)


@router.put("/{timetable_id}", response_model=TimetableResponse)
async def update_timetable(timetable_id: str, req: TimetableUpdate, user_id: str = Depends(get_current_user_id)):
    """Updates timetable."""
    return await timetable_service.update_timetable(timetable_id, user_id, req)


@router.delete("/{timetable_id}", status_code=200)
async def delete_timetable(timetable_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes timetable."""
    await timetable_service.delete_timetable(timetable_id, user_id)
    return success_response({"message": "Timetable deleted successfully."})
