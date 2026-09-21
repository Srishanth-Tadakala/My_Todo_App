"""
Internship Applications Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.common import PaginatedResponse
from app.schemas.internship import InternshipCreate, InternshipResponse, InternshipStatus, InternshipUpdate
from app.services.internship_service import internship_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/internships", tags=["Internships"])


@router.get("", response_model=PaginatedResponse[InternshipResponse])
async def list_internships(
    status: Optional[InternshipStatus] = Query(None),
    sort_by: str = Query("application_deadline"),
    ascending: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists internship applications with status filtering and pagination."""
    items, total = await internship_service.list_internships(
        user_id=user_id,
        status=status.value if status else None,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=InternshipResponse, status_code=201)
async def create_internship(req: InternshipCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new internship application tracker entry."""
    return await internship_service.create_internship(user_id, req)


@router.get("/{internship_id}", response_model=InternshipResponse)
async def get_internship(internship_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves internship application by ID."""
    return await internship_service.get_internship(internship_id, user_id)


@router.put("/{internship_id}", response_model=InternshipResponse)
async def update_internship(
    internship_id: str,
    req: InternshipUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates internship application status (APPLIED, INTERVIEW, OFFER, etc.)."""
    return await internship_service.update_internship(internship_id, user_id, req)


@router.delete("/{internship_id}", status_code=200)
async def delete_internship(internship_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes an internship application tracker."""
    await internship_service.delete_internship(internship_id, user_id)
    return success_response({"message": "Internship deleted successfully."})
