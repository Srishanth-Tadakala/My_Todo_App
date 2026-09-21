"""
Projects Repository
"""

from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class ProjectRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("projects", has_soft_delete=True)

    async def get_by_id(self, project_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(project_id, user_id)

    async def list_projects(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        ascending: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        filters = {"status": status} if status else None
        return await self.repo.list_all(
            user_id=user_id,
            filters=filters,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(data)

    async def update(self, project_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(project_id, user_id, data)

    async def delete(self, project_id: str, user_id: str, soft: bool = True) -> bool:
        return await self.repo.delete(project_id, user_id, soft=soft)
