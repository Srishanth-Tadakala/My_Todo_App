"""
Projects Router
"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from app.core.responses import success_response
from app.dependencies import get_current_user_id
from app.schemas.common import PaginatedResponse
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectStatus, ProjectUpdate
from app.services.project_service import project_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get("", response_model=PaginatedResponse[ProjectResponse])
async def list_projects(
    status: Optional[ProjectStatus] = Query(None),
    sort_by: str = Query("created_at"),
    ascending: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Lists projects with completion percentages, task metrics, and pagination."""
    items, total = await project_service.list_projects(
        user_id=user_id,
        status=status.value if status else None,
        sort_by=sort_by,
        ascending=ascending,
        page=page,
        page_size=page_size,
    )
    return build_paginated_response(items, total, page, page_size)


@router.post("", response_model=ProjectResponse, status_code=201)
async def create_project(req: ProjectCreate, user_id: str = Depends(get_current_user_id)):
    """Creates a new project."""
    return await project_service.create_project(user_id, req)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: str, user_id: str = Depends(get_current_user_id)):
    """Retrieves project details and task completion stats."""
    return await project_service.get_project(project_id, user_id)


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    req: ProjectUpdate,
    user_id: str = Depends(get_current_user_id),
):
    """Updates project information."""
    return await project_service.update_project(project_id, user_id, req)


@router.delete("/{project_id}", status_code=200)
async def delete_project(project_id: str, user_id: str = Depends(get_current_user_id)):
    """Soft deletes a project."""
    await project_service.delete_project(project_id, user_id)
    return success_response({"message": "Project deleted successfully."})
