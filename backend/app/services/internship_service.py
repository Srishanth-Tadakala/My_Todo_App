"""
Internship Service
"""

from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import internship_repo
from app.schemas.internship import InternshipCreate, InternshipResponse, InternshipUpdate
from app.schemas.reminder import EntityType, ReminderType
from app.services.reminder_service import reminder_service
from app.utils.datetime import parse_datetime


class InternshipService:
    def __init__(self, i_repo=None, r_service=None):
        self.repo = i_repo or internship_repo
        self.reminder_service = r_service or reminder_service

    async def get_internship(self, internship_id: str, user_id: str) -> InternshipResponse:
        item = await self.repo.get_by_id(internship_id, user_id)
        if not item:
            raise NotFoundException("Internship not found.", code="INTERNSHIP_NOT_FOUND")
        return InternshipResponse(**item)

    async def list_internships(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "application_deadline",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[InternshipResponse], int]:
        items, total = await self.repo.list_internships(
            user_id=user_id,
            status=status,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        return [InternshipResponse(**i) for i in items], total

    async def create_internship(self, user_id: str, req: InternshipCreate) -> InternshipResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        data["status"] = req.status.value if req.status else "SAVED"
        res = await self.repo.create(data)
        intern_id = str(res["id"])

        if req.application_deadline:
            dl_dt = parse_datetime(req.application_deadline)
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.INTERNSHIP,
                entity_id=intern_id,
                target_time_utc=dl_dt,
                minutes_before=2880,  # 2 days
                reminder_type=ReminderType.DEADLINE_APPROACHING,
            )

        if req.interview_at:
            inv_dt = parse_datetime(req.interview_at)
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.INTERNSHIP,
                entity_id=intern_id,
                target_time_utc=inv_dt,
                minutes_before=120,  # 2 hours
                reminder_type=ReminderType.INTERVIEW_UPCOMING,
            )

        return InternshipResponse(**res)

    async def update_internship(self, internship_id: str, user_id: str, req: InternshipUpdate) -> InternshipResponse:
        data = req.model_dump(exclude_unset=True)
        if "status" in data and data["status"]:
            data["status"] = req.status.value
            if data["status"] in ("ACCEPTED", "REJECTED", "WITHDRAWN"):
                await self.reminder_service.cancel_for_entity(user_id, EntityType.INTERNSHIP.value, internship_id)

        res = await self.repo.update(internship_id, user_id, data)
        if not res:
            raise NotFoundException("Internship not found.", code="INTERNSHIP_NOT_FOUND")
        return InternshipResponse(**res)

    async def delete_internship(self, internship_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete(internship_id, user_id)
        if not deleted:
            raise NotFoundException("Internship not found.", code="INTERNSHIP_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.INTERNSHIP.value, internship_id)
        return True


internship_service = InternshipService()
