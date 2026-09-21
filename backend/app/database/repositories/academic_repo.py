"""
Academic Repositories (Assignments and Exams)
"""

from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class AssignmentRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("assignments", has_soft_delete=False)

    async def get_by_id(self, assignment_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(assignment_id, user_id)

    async def list_assignments(
        self,
        user_id: str,
        subject_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        sort_by: str = "due_at",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        filters: Dict[str, Any] = {}
        if subject_id:
            filters["subject_id"] = subject_id
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority

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

    async def update(self, assignment_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(assignment_id, user_id, data)

    async def delete(self, assignment_id: str, user_id: str) -> bool:
        return await self.repo.delete(assignment_id, user_id, soft=False)


class ExamRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("exams", has_soft_delete=False)

    async def get_by_id(self, exam_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(exam_id, user_id)

    async def list_exams(
        self,
        user_id: str,
        subject_id: Optional[str] = None,
        sort_by: str = "exam_date",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        filters: Dict[str, Any] = {}
        if subject_id:
            filters["subject_id"] = subject_id

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

    async def update(self, exam_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(exam_id, user_id, data)

    async def delete(self, exam_id: str, user_id: str) -> bool:
        return await self.repo.delete(exam_id, user_id, soft=False)
