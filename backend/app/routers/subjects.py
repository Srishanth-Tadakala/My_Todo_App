"""
Academic Subjects Router
"""

from typing import List
from fastapi import APIRouter, Depends
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate
from app.services.subject_service import subject_service

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("", response_model=List[SubjectResponse])
async def list_subjects(user_id: str = Depends(get_current_user_id)):
    """Lists all academic subjects for the user."""
    return await subject_service.list_subjects(user_id)


@router.post("", response_model=SubjectResponse, status_code=201)
async def create_subject(req: SubjectCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new subject."""
    return await subject_service.create_subject(user_id, req)


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(subject_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves a single subject by ID."""
    return await subject_service.get_subject(subject_id, user_id)


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(subject_id: str, req: SubjectUpdate, user_id: str = Depends(get_current_user_id)):
    """Updates a subject."""
    return await subject_service.update_subject(subject_id, user_id, req)


@router.delete("/{subject_id}", status_code=200)
async def delete_subject(subject_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes a subject."""
    await subject_service.delete_subject(subject_id, user_id)
    return success_response({"message": "Subject deleted successfully."})
