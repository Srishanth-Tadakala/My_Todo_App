"""
Exams Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.common import PaginatedResponse
from app.schemas.exam import ExamCreate, ExamResponse, ExamUpdate
from app.services.exam_service import exam_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.get("", response_model=PaginatedResponse[ExamResponse])
async def list_exams(
    subject_id: Optional[str] = Query(None),
    sort_by: str = Query("exam_date"),
    ascending: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists scheduled exams with subject filtering and pagination."""
    items, total = await exam_service.list_exams(
        user_id=user_id,
        subject_id=subject_id,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=ExamResponse, status_code=201)
async def create_exam(req: ExamCreate, user_id: str = Depends(get_current_user_id)):
    """Creates an exam with customizable multi-tier reminder offsets (e.g. 7d, 1d, 2h)."""
    return await exam_service.create_exam(user_id, req)


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(exam_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves exam details by ID."""
    return await exam_service.get_exam(exam_id, user_id)


@router.put("/{exam_id}", response_model=ExamResponse)
async def update_exam(exam_id: str, req: ExamUpdate, user_id: str = Depends(get_current_user_id)):
    """Updates exam date, room, syllabus, or reminder offsets."""
    return await exam_service.update_exam(exam_id, user_id, req)


@router.delete("/{exam_id}", status_code=200)
async def delete_exam(exam_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes an exam and cancels its reminders."""
    await exam_service.delete_exam(exam_id, user_id)
    return success_response({"message": "Exam deleted successfully."})
