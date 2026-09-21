"""
Assignments Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.assignment import AssignmentCreate, AssignmentPriority, AssignmentResponse, AssignmentStatus, AssignmentUpdate
from app.schemas.common import PaginatedResponse
from app.services.assignment_service import assignment_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.get("", response_model=PaginatedResponse[AssignmentResponse])
async def list_assignments(
    subject_id: Optional[str] = Query(None),
    status: Optional[AssignmentStatus] = Query(None),
    priority: Optional[AssignmentPriority] = Query(None),
    sort_by: str = Query("due_at"),
    ascending: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists assignments with subject filtering, status, priority, and pagination."""
    items, total = await assignment_service.list_assignments(
        user_id=user_id,
        subject_id=subject_id,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=AssignmentResponse, status_code=201)
async def create_assignment(req: AssignmentCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new assignment and auto-configures deadline reminders."""
    return await assignment_service.create_assignment(user_id, req)


@router.get("/{assignment_id}", response_model=AssignmentResponse)
async def get_assignment(assignment_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves assignment by ID."""
    return await assignment_service.get_assignment(assignment_id, user_id)


@router.put("/{assignment_id}", response_model=AssignmentResponse)
async def update_assignment(
    assignment_id: str,
    req: AssignmentUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates assignment details, submission url, or status."""
    return await assignment_service.update_assignment(assignment_id, user_id, req)


@router.delete("/{assignment_id}", status_code=200)
async def delete_assignment(assignment_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes an assignment."""
    await assignment_service.delete_assignment(assignment_id, user_id)
    return success_response({"message": "Assignment deleted successfully."})
