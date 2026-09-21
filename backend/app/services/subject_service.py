"""
Academic Subject Service
"""

from typing import List, Optional
from app.core.exceptions import NotFoundException
from app.database.repositories import subject_repo
from app.schemas.subject import SubjectCreate, SubjectResponse, SubjectUpdate


class SubjectService:
    def __init__(self, s_repo=None):
        self.subject_repo = s_repo or subject_repo

    async def get_subject(self, subject_id: str, user_id: str) -> SubjectResponse:
        item = await self.subject_repo.get_by_id(subject_id, user_id)
        if not item:
            raise NotFoundException("Subject not found.", code="SUBJECT_NOT_FOUND")
        return SubjectResponse(**item)

    async def list_subjects(self, user_id: str) -> List[SubjectResponse]:
        items = await self.subject_repo.list_for_user(user_id)
        return [SubjectResponse(**i) for i in items]

    async def create_subject(self, user_id: str, req: SubjectCreate) -> SubjectResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        res = await self.subject_repo.create(data)
        return SubjectResponse(**res)

    async def update_subject(self, subject_id: str, user_id: str, req: SubjectUpdate) -> SubjectResponse:
        data = req.model_dump(exclude_unset=True)
        res = await self.subject_repo.update(subject_id, user_id, data)
        if not res:
            raise NotFoundException("Subject not found.", code="SUBJECT_NOT_FOUND")
        return SubjectResponse(**res)

    async def delete_subject(self, subject_id: str, user_id: str) -> bool:
        deleted = await self.subject_repo.delete(subject_id, user_id)
        if not deleted:
            raise NotFoundException("Subject not found.", code="SUBJECT_NOT_FOUND")
        return True


subject_service = SubjectService()
