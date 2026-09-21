"""
Career Repositories (Hackathons, Certifications, Internships)
"""

from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class HackathonRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("hackathons", has_soft_delete=False)

    async def get_by_id(self, hackathon_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(hackathon_id, user_id)

    async def list_hackathons(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "submission_deadline",
        ascending: bool = True,
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

    async def update(self, hackathon_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(hackathon_id, user_id, data)

    async def delete(self, hackathon_id: str, user_id: str) -> bool:
        return await self.repo.delete(hackathon_id, user_id, soft=False)


class CertificationRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("certifications", has_soft_delete=False)

    async def get_by_id(self, cert_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(cert_id, user_id)

    async def list_certifications(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "exam_date",
        ascending: bool = True,
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

    async def update(self, cert_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(cert_id, user_id, data)

    async def delete(self, cert_id: str, user_id: str) -> bool:
        return await self.repo.delete(cert_id, user_id, soft=False)


class InternshipRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("internships", has_soft_delete=False)

    async def get_by_id(self, internship_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(internship_id, user_id)

    async def list_internships(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "application_deadline",
        ascending: bool = True,
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

    async def update(self, internship_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(internship_id, user_id, data)

    async def delete(self, internship_id: str, user_id: str) -> bool:
        return await self.repo.delete(internship_id, user_id, soft=False)
