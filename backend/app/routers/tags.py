"""
Tags Router
"""

from typing import List
from fastapi import APIRouter, Depends
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.tag import TagCreate, TagResponse
from app.services.todo_service import todo_service

router = APIRouter(prefix="/tags", tags=["Tags"])


@router.get("", response_model=List[TagResponse])
async def list_tags(user_id: str = Depends(get_current_user_id)):
    """Retrieves all user tags."""
    return await todo_service.list_tags(user_id)


@router.post("", response_model=TagResponse, status_code=201)
async def create_tag(req: TagCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new tag."""
    return await todo_service.create_tag(user_id, req)


@router.delete("/{tag_id}", status_code=200)
async def delete_tag(tag_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes a tag."""
    await todo_service.delete_tag(tag_id, user_id)
    return success_response({"message": "Tag deleted successfully."})
