"""
Todos and Subtasks Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Header, Query
from app.core.idempotency import idempotency_cache
from app.core.responses import success_response
from app.dependencies import get_current_user_id, get_idempotency_key
from app.schemas.common import PaginatedResponse
from app.schemas.todo import (
    SubtaskCreate, SubtaskResponse, SubtaskUpdate, TodoCreate,
    TodoPostpone, TodoPriority, TodoReschedule, TodoResponse, TodoStatus, TodoUpdate
)
from app.services.todo_service import todo_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/todos", tags=["Todos"])


@router.get("", response_model=PaginatedResponse[TodoResponse])
async def list_todos(
    list_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    status: Optional[TodoStatus] = Query(None),
    priority: Optional[TodoPriority] = Query(None),
    q: Optional[str] = Query(None),
    sort_by: str = Query("due_at"),
    ascending: bool = Query(True),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists todos with filtering, sorting, subtasks, tags, and pagination."""
    items, total = await todo_service.list_todos(
        user_id=user_id,
        list_id=list_id,
        project_id=project_id,
        status=status.value if status else None,
        priority=priority.value if priority else None,
        search_query=q,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=TodoResponse, status_code=201)
async def create_todo(
    req: TodoCreate,
    idempotency_key: Optional[str] = Depends(get_idempotency_key),
    user_id: str = Depends(get_current_user_id),
):
    """Creates a new todo with optional subtasks, tags, and automatic reminders."""
    if idempotency_key:
        cached = idempotency_cache.get(f"todo:{user_id}:{idempotency_key}")
        if cached:
            return cached[1]

    created = await todo_service.create_todo(user_id, req)

    if idempotency_key:
        idempotency_cache.set(f"todo:{user_id}:{idempotency_key}", 201, created)

    return created


@router.get("/{todo_id}", response_model=TodoResponse)
async def get_todo(
    todo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Retrieves a single todo by ID."""
    return await todo_service.get_todo(todo_id, user_id)


@router.put("/{todo_id}", response_model=TodoResponse)
async def update_todo(
    todo_id: str,
    req: TodoUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates todo details, priority, due date, or tags."""
    return await todo_service.update_todo(todo_id, user_id, req)


@router.delete("/{todo_id}", status_code=200)
async def delete_todo(
    todo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Soft deletes a todo."""
    await todo_service.delete_todo(todo_id, user_id)
    return success_response({"message": "Todo deleted successfully."})


@router.post("/{todo_id}/complete", response_model=TodoResponse)
async def complete_todo(
    todo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Marks todo as completed and cancels pending reminders."""
    return await todo_service.complete_todo(todo_id, user_id)


@router.post("/{todo_id}/reopen", response_model=TodoResponse)
async def reopen_todo(
    todo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Reopens a completed or cancelled todo."""
    return await todo_service.reopen_todo(todo_id, user_id)


@router.post("/{todo_id}/cancel", response_model=TodoResponse)
async def cancel_todo(
    todo_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Cancels a todo and revokes reminders."""
    return await todo_service.cancel_todo(todo_id, user_id)


@router.post("/{todo_id}/postpone", response_model=TodoResponse)
async def postpone_todo(
    todo_id: str,
    minutes: int = Query(1440, ge=1),
    user_id: str = Depends(get_current_user_id),
):
    """Postpones a todo by N minutes (default 24 hours), increments postpone count."""
    return await todo_service.postpone_todo(todo_id, user_id, minutes=minutes)


@router.post("/{todo_id}/reschedule", response_model=TodoResponse)
async def reschedule_todo(
    todo_id: str,
    req: TodoReschedule,
    user_id: str = Depends(get_current_user_id),
):
    """Sets a new due date and updates reminders."""
    return await todo_service.reschedule_todo(todo_id, user_id, req)


# Subtasks Endpoints
@router.post("/{todo_id}/subtasks", response_model=SubtaskResponse, status_code=201)
async def create_subtask(
    todo_id: str,
    req: SubtaskCreate,
    user_id: str = Depends(get_current_user_id),
):
    """Adds a subtask to a todo."""
    return await todo_service.create_subtask(todo_id, user_id, req)


@router.put("/subtasks/{subtask_id}", response_model=SubtaskResponse)
async def update_subtask(
    subtask_id: str,
    req: SubtaskUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates subtask title, order, or completion status."""
    return await todo_service.update_subtask(subtask_id, user_id, req)


@router.delete("/subtasks/{subtask_id}", status_code=200)
async def delete_subtask(
    subtask_id: str,
    user_id: str = Depends(get_current_user_id),
):
    """Deletes a subtask."""
    await todo_service.delete_subtask(subtask_id, user_id)
    return success_response({"message": "Subtask deleted successfully."})
