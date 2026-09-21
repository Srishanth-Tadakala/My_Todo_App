"""
Personal Events Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.common import PaginatedResponse
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.services.event_service import event_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/events", tags=["Events"])


@router.get("", response_model=PaginatedResponse[EventResponse])
async def list_events(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists personal events within optional date boundaries."""
    items, total = await event_service.list_events(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=EventResponse, status_code=201)
async def create_event(req: EventCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new personal event with start-time reminder."""
    return await event_service.create_event(user_id, req)


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves personal event by ID."""
    return await event_service.get_event(event_id, user_id)


@router.put("/{event_id}", response_model=EventResponse)
async def update_event(
    event_id: str,
    req: EventUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates personal event timing, location, or details."""
    return await event_service.update_event(event_id, user_id, req)


@router.delete("/{event_id}", status_code=200)
async def delete_event(event_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes an event and cancels reminders."""
    await event_service.delete_event(event_id, user_id)
    return success_response({"message": "Event deleted successfully."})
