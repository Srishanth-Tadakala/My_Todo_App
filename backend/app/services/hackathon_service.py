"""
Hackathon Service
"""

from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import hackathon_repo
from app.schemas.hackathon import HackathonCreate, HackathonResponse, HackathonUpdate
from app.schemas.reminder import EntityType, ReminderType
from app.services.reminder_service import reminder_service
from app.utils.datetime import parse_datetime


class HackathonService:
    def __init__(self, h_repo=None, r_service=None):
        self.repo = h_repo or hackathon_repo
        self.reminder_service = r_service or reminder_service

    async def get_hackathon(self, hackathon_id: str, user_id: str) -> HackathonResponse:
        item = await self.repo.get_by_id(hackathon_id, user_id)
        if not item:
            raise NotFoundException("Hackathon not found.", code="HACKATHON_NOT_FOUND")
        return HackathonResponse(**item)

    async def list_hackathons(
        self,
        user_id: str,
        status: Optional[str] = None,
        sort_by: str = "submission_deadline",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[HackathonResponse], int]:
        items, total = await self.repo.list_hackathons(
            user_id=user_id,
            status=status,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        return [HackathonResponse(**i) for i in items], total

    async def create_hackathon(self, user_id: str, req: HackathonCreate) -> HackathonResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        data["status"] = req.status.value if req.status else "INTERESTED"
        res = await self.repo.create(data)
        hack_id = str(res["id"])

        # Schedule reminder for submission deadline (e.g. 3 days before)
        sub_dt = parse_datetime(req.submission_deadline)
        await self.reminder_service.schedule_entity_reminder(
            user_id=user_id,
            entity_type=EntityType.HACKATHON,
            entity_id=hack_id,
            target_time_utc=sub_dt,
            minutes_before=4320,  # 3 days
            reminder_type=ReminderType.DEADLINE_APPROACHING,
        )

        return HackathonResponse(**res)

    async def update_hackathon(self, hackathon_id: str, user_id: str, req: HackathonUpdate) -> HackathonResponse:
        data = req.model_dump(exclude_unset=True)
        if "status" in data and data["status"]:
            data["status"] = req.status.value
            if data["status"] in ("SUBMITTED", "COMPLETED", "CANCELLED"):
                await self.reminder_service.cancel_for_entity(user_id, EntityType.HACKATHON.value, hackathon_id)

        res = await self.repo.update(hackathon_id, user_id, data)
        if not res:
            raise NotFoundException("Hackathon not found.", code="HACKATHON_NOT_FOUND")

        if "submission_deadline" in data and data["submission_deadline"]:
            sub_dt = parse_datetime(data["submission_deadline"])
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.HACKATHON,
                entity_id=hackathon_id,
                target_time_utc=sub_dt,
                minutes_before=4320,
                reminder_type=ReminderType.DEADLINE_APPROACHING,
            )

        return HackathonResponse(**res)

    async def delete_hackathon(self, hackathon_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete(hackathon_id, user_id)
        if not deleted:
            raise NotFoundException("Hackathon not found.", code="HACKATHON_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.HACKATHON.value, hackathon_id)
        return True


hackathon_service = HackathonService()
