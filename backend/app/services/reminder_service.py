"""
Reminder Service
Manages concrete reminder generation, quiet-hours shifting, and scheduling.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from app.core.exceptions import NotFoundException
from app.database.repositories import reminder_repo, user_repo
from app.schemas.reminder import (
    ChannelType, EntityType, ReminderCreate, ReminderResponse, ReminderStatus, ReminderType, ReminderUpdate
)
from app.utils.datetime import adjust_for_quiet_hours, now_utc, parse_datetime


class ReminderService:
    def __init__(self, r_repo=None, u_repo=None):
        self.reminder_repo = r_repo or reminder_repo
        self.user_repo = u_repo or user_repo

    async def get_reminder(self, reminder_id: str, user_id: str) -> ReminderResponse:
        item = await self.reminder_repo.get_by_id(reminder_id, user_id)
        if not item:
            raise NotFoundException("Reminder not found.", code="REMINDER_NOT_FOUND")
        return ReminderResponse(**item)

    async def list_for_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[ReminderResponse], int]:
        items, total = await self.reminder_repo.list_for_user(
            user_id=user_id,
            status=status,
            entity_type=entity_type,
            page=page,
            page_size=page_size,
        )
        return [ReminderResponse(**i) for i in items], total

    async def create_reminder(self, user_id: str, req: ReminderCreate) -> ReminderResponse:
        remind_dt = parse_datetime(req.remind_at)

        # Apply quiet hours policy
        settings = await self.user_repo.get_settings(user_id)
        if settings and settings.get("quiet_hours_enabled"):
            remind_dt = adjust_for_quiet_hours(
                remind_dt,
                settings.get("timezone", "UTC"),
                settings.get("quiet_hours_start", "22:00:00"),
                settings.get("quiet_hours_end", "07:00:00"),
            )

        data = {
            "user_id": user_id,
            "entity_type": req.entity_type.value,
            "entity_id": req.entity_id,
            "reminder_type": req.reminder_type.value if req.reminder_type else "DUE_SOON",
            "remind_at": remind_dt.isoformat(),
            "channel": req.channel.value if req.channel else "PUSH",
            "status": "PENDING",
            "attempt_count": 0,
        }
        created = await self.reminder_repo.create(data)
        return ReminderResponse(**created)

    async def update_reminder(self, reminder_id: str, user_id: str, req: ReminderUpdate) -> ReminderResponse:
        data = req.model_dump(exclude_unset=True)
        if "remind_at" in data and data["remind_at"]:
            dt = parse_datetime(data["remind_at"])
            settings = await self.user_repo.get_settings(user_id)
            if settings and settings.get("quiet_hours_enabled"):
                dt = adjust_for_quiet_hours(
                    dt,
                    settings.get("timezone", "UTC"),
                    settings.get("quiet_hours_start", "22:00:00"),
                    settings.get("quiet_hours_end", "07:00:00"),
                )
            data["remind_at"] = dt.isoformat()

        updated = await self.reminder_repo.update(reminder_id, user_id, data)
        if not updated:
            raise NotFoundException("Reminder not found.", code="REMINDER_NOT_FOUND")
        return ReminderResponse(**updated)

    async def cancel_for_entity(self, user_id: str, entity_type: str, entity_id: str) -> int:
        """Cancels all active reminders for a given entity."""
        return await self.reminder_repo.cancel_for_entity(user_id, entity_type, entity_id)

    async def schedule_entity_reminder(
        self,
        user_id: str,
        entity_type: EntityType,
        entity_id: str,
        target_time_utc: datetime,
        minutes_before: int,
        reminder_type: ReminderType = ReminderType.DUE_SOON,
    ) -> Optional[ReminderResponse]:
        """Calculates remind_at offset and creates concrete reminder if in future."""
        remind_time = target_time_utc - timedelta(minutes=minutes_before)
        if remind_time <= now_utc():
            # Already in the past
            return None

        # Cancel any previous pending reminders for this entity
        await self.cancel_for_entity(user_id, entity_type.value, entity_id)

        req = ReminderCreate(
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_type=reminder_type,
            remind_at=remind_time.isoformat(),
            channel=ChannelType.PUSH,
        )
        return await self.create_reminder(user_id, req)


reminder_service = ReminderService()
