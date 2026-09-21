"""
Todo Lists Router
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.list import TodoListCreate, TodoListResponse, TodoListStats, TodoListUpdate
from app.services.list_service import todo_list_service

router = APIRouter(prefix="/lists", tags=["Lists"])


@router.get("", response_model=List[TodoListResponse])
async def list_todo_lists(
    include_archived: bool = Query(False),
    user_id: str = Depends(get_current_user_id),
):
    """Retrieves all todo lists for the user."""
    return await todo_list_service.list_for_user(user_id, include_archived=include_archived)


@router.post("", response_model=TodoListResponse, status_code=201)
async def create_todo_list(
    req: TodoListCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Creates a new todo list."""
    return await todo_list_service.create_list(user_id, req)


@router.get("/{list_id}", response_model=TodoListResponse)
async def get_todo_list(
    list_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Retrieves a single list by ID with its statistics."""
    return await todo_list_service.get_list(list_id, user_id)


@router.put("/{list_id}", response_model=TodoListResponse)
async def update_todo_list(
    list_id: str,
    req: TodoListUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates a todo list."""
    return await todo_list_service.update_list(list_id, user_id, req)


@router.delete("/{list_id}", status_code=200)
async def delete_todo_list(
    list_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Soft deletes a todo list."""
    await todo_list_service.delete_list(list_id, user_id)
    return success_response({"message": "List deleted successfully."})


@router.post("/{list_id}/archive", response_model=TodoListResponse)
async def archive_todo_list(
    list_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Archives a todo list."""
    return await todo_list_service.archive_list(list_id, user_id)


@router.post("/{list_id}/restore", response_model=TodoListResponse)
async def restore_todo_list(
    list_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Restores an archived todo list."""
    return await todo_list_service.restore_list(list_id, user_id)


@router.post("/reorder", response_model=List[TodoListResponse])
async def reorder_todo_lists(
    ordered_ids: List[str],
    user_id: str = Depends(get_current_user_id),
):
    """Reorders lists according to the given array of IDs."""
    return await todo_list_service.reorder_lists(user_id, ordered_ids)


@router.get("/{list_id}/stats", response_model=TodoListStats)
async def get_list_stats(
    list_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Returns task counts and completion rate for the list."""
    return await todo_list_service.get_list_stats(list_id, user_id)
