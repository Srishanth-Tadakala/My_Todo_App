"""
Hackathons Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.common import PaginatedResponse
from app.schemas.hackathon import HackathonCreate, HackathonResponse, HackathonStatus, HackathonUpdate
from app.services.hackathon_service import hackathon_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/hackathons", tags=["Hackathons"])


@router.get("", response_model=PaginatedResponse[HackathonResponse])
async def list_hackathons(
    status: Optional[HackathonStatus] = Query(None),
    sort_by: str = Query("submission_deadline"),
    ascending: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists hackathons with status filtering and pagination."""
    items, total = await hackathon_service.list_hackathons(
        user_id=user_id,
        status=status.value if status else None,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=HackathonResponse, status_code=201)
async def create_hackathon(req: HackathonCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new hackathon entry and schedules deadline reminders."""
    return await hackathon_service.create_hackathon(user_id, req)


@router.get("/{hackathon_id}", response_model=HackathonResponse)
async def get_hackathon(hackathon_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves hackathon by ID."""
    return await hackathon_service.get_hackathon(hackathon_id, user_id)


@router.put("/{hackathon_id}", response_model=HackathonResponse)
async def update_hackathon(
    hackathon_id: str,
    req: HackathonUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates hackathon status, team name, or deadline."""
    return await hackathon_service.update_hackathon(hackathon_id, user_id, req)


@router.delete("/{hackathon_id}", status_code=200)
async def delete_hackathon(hackathon_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes a hackathon."""
    await hackathon_service.delete_hackathon(hackathon_id, user_id)
    return success_response({"message": "Hackathon deleted successfully."})
