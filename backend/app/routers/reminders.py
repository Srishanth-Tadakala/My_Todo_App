"""
Reminders Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.idempotency import idempotency_cache
from app.core.responses import success_response
from app.dependencies import get_current_user_id, get_idempotency_key
from app.schemas.common import PaginatedResponse
from app.schemas.reminder import ReminderCreate, ReminderResponse, ReminderStatus, ReminderUpdate
from app.services.reminder_service import reminder_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@router.get("", response_model=PaginatedResponse[ReminderResponse])
async def list_reminders(
    status: Optional[ReminderStatus] = Query(None),
    entity_type: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists reminders for the authenticated user."""
    items, total = await reminder_service.list_for_user(
        user_id=user_id,
        status=status.value if status else None,
        entity_type=entity_type,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=ReminderResponse, status_code=201)
async def create_reminder(
    req: ReminderCreate,
    idempotency_key: Optional[str] = Depends(get_idempotency_key),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a custom rule-based reminder with quiet hours shifting."""
    if idempotency_key:
        cached = idempotency_cache.get(f"reminder:{user_id}:{idempotency_key}")
        if cached:
            return cached[1]

    created = await reminder_service.create_reminder(user_id, req)

    if idempotency_key:
        idempotency_cache.set(f"reminder:{user_id}:{idempotency_key}", 201, created)

    return created


@router.get("/{reminder_id}", response_model=ReminderResponse)
async def get_reminder(reminder_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves reminder details by ID."""
    return await reminder_service.get_reminder(reminder_id, user_id)


@router.put("/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: str,
    req: ReminderUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates reminder time, channel, or status."""
    return await reminder_service.update_reminder(reminder_id, user_id, req)


@router.delete("/{reminder_id}", status_code=200)
async def cancel_reminder(reminder_id: str, user_id: str = Depends(get_current_user_id)):
    """Cancels a reminder."""
    await reminder_service.update_reminder(reminder_id, user_id, ReminderUpdate(status=ReminderStatus.CANCELLED))
    return success_response({"message": "Reminder cancelled successfully."})
