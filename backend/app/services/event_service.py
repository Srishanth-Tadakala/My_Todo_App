"""
Personal Events Service
"""

from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import event_repo
from app.schemas.event import EventCreate, EventResponse, EventUpdate
from app.schemas.reminder import EntityType, ReminderType
from app.services.reminder_service import reminder_service
from app.utils.datetime import parse_datetime


class EventService:
    def __init__(self, e_repo=None, r_service=None):
        self.repo = e_repo or event_repo
        self.reminder_service = r_service or reminder_service

    async def get_event(self, event_id: str, user_id: str) -> EventResponse:
        item = await self.repo.get_by_id(event_id, user_id)
        if not item:
            raise NotFoundException("Event not found.", code="EVENT_NOT_FOUND")
        return EventResponse(**item)

    async def list_events(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[EventResponse], int]:
        items, total = await self.repo.list_events(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            page=page,
            page_size=page_size,
        )
        return [EventResponse(**i) for i in items], total

    async def create_event(self, user_id: str, req: EventCreate) -> EventResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        res = await self.repo.create(data)
        event_id = str(res["id"])

        if req.reminder_enabled and req.start_at:
            st_dt = parse_datetime(req.start_at)
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.EVENT,
                entity_id=event_id,
                target_time_utc=st_dt,
                minutes_before=req.reminder_minutes,
                reminder_type=ReminderType.EVENT_STARTING,
            )

        return EventResponse(**res)

    async def update_event(self, event_id: str, user_id: str, req: EventUpdate) -> EventResponse:
        data = req.model_dump(exclude_unset=True)
        res = await self.repo.update(event_id, user_id, data)
        if not res:
            raise NotFoundException("Event not found.", code="EVENT_NOT_FOUND")

        if res.get("reminder_enabled") and res.get("start_at"):
            st_dt = parse_datetime(res["start_at"])
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.EVENT,
                entity_id=event_id,
                target_time_utc=st_dt,
                minutes_before=res.get("reminder_minutes", 30),
                reminder_type=ReminderType.EVENT_STARTING,
            )
        elif not res.get("reminder_enabled"):
            await self.reminder_service.cancel_for_entity(user_id, EntityType.EVENT.value, event_id)

        return EventResponse(**res)

    async def delete_event(self, event_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete(event_id, user_id)
        if not deleted:
            raise NotFoundException("Event not found.", code="EVENT_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.EVENT.value, event_id)
        return True


event_service = EventService()
