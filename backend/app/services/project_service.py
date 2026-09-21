"""
Project Service
Computes dynamic task metrics and completion progress.
"""

from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import project_repo, todo_repo
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectStats, ProjectUpdate


class ProjectService:
    def __init__(self, p_repo=None, t_repo=None):
        self.project_repo = p_repo or project_repo
        self.todo_repo = t_repo or todo_repo

    async def _calculate_stats(self, project_id: str, user_id: str) -> ProjectStats:
        todos, _ = await self.todo_repo.list_todos(user_id=user_id, project_id=project_id, page_size=1000)
        total = len(todos)
        completed = sum(1 for t in todos if t.get("status") == "COMPLETED")
        pending = total - completed
        percentage = (completed / total * 100.0) if total > 0 else 0.0
        return ProjectStats(
            total_tasks=total,
            completed_tasks=completed,
            pending_tasks=pending,
            completion_percentage=round(percentage, 1),
        )

    async def get_project(self, project_id: str, user_id: str) -> ProjectResponse:
        item = await self.project_repo.get_by_id(project_id, user_id)
        if not item:
            raise NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")
        stats = await self._calculate_stats(project_id, user_id)
        return ProjectResponse(**item, stats=stats)

    async def list_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        ascending: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[ProjectResponse], int]:
        items, total = await self.project_repo.list_projects(
            user_id=user_id,
            status=status,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        results = []
        for it in items:
            stats = await self._calculate_stats(str(it["id"]), user_id)
            results.append(ProjectResponse(**it, stats=stats))
        return results, total

    async def create_project(self, user_id: str, req: ProjectCreate) -> ProjectResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        data["status"] = req.status.value if req.status else "PLANNING"
        res = await self.project_repo.create(data)
        return ProjectResponse(**res, stats=ProjectStats())

    async def update_project(self, project_id: str, user_id: str, req: ProjectUpdate) -> ProjectResponse:
        data = req.model_dump(exclude_unset=True)
        if "status" in data and data["status"]:
            data["status"] = req.status.value
        res = await self.project_repo.update(project_id, user_id, data)
        if not res:
            raise NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")
        stats = await self._calculate_stats(project_id, user_id)
        return ProjectResponse(**res, stats=stats)

    async def delete_project(self, project_id: str, user_id: str, soft: bool = True) -> bool:
        deleted = await self.project_repo.delete(project_id, user_id, soft=soft)
        if not deleted:
            raise NotFoundException("Project not found.", code="PROJECT_NOT_FOUND")
        return True


project_service = ProjectService()
