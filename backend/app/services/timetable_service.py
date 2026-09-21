"""
Timetable and Schedule Service
Handles Timetables, Recurring Schedule Items, Conflict Detection, and Exceptions.
"""

from datetime import date, datetime, time, timedelta
from typing import Any, Dict, List, Optional
from app.core.exceptions import NotFoundException
from app.database.repositories import timetable_repo
from app.schemas.common import ConflictCheckResult, ConflictItem
from app.schemas.timetable import (
    ScheduleExceptionCreate, ScheduleExceptionResponse,
    ScheduleItemCreate, ScheduleItemResponse, ScheduleItemUpdate,
    ScheduleOccurrenceResponse, TimetableCreate, TimetableResponse, TimetableUpdate
)
from app.utils.datetime import parse_time
from app.utils.recurrence import check_time_conflict, expand_schedule_item_occurrences


class TimetableService:
    def __init__(self, t_repo=None):
        self.repo = t_repo or timetable_repo

    # Timetable
    async def get_timetable(self, timetable_id: str, user_id: str) -> TimetableResponse:
        item = await self.repo.get_timetable(timetable_id, user_id)
        if not item:
            raise NotFoundException("Timetable not found.", code="TIMETABLE_NOT_FOUND")
        return TimetableResponse(**item)

    async def get_active_timetable(self, user_id: str) -> Optional[TimetableResponse]:
        item = await self.repo.get_active_timetable(user_id)
        return TimetableResponse(**item) if item else None

    async def list_timetables(self, user_id: str) -> List[TimetableResponse]:
        items = await self.repo.list_timetables(user_id)
        return [TimetableResponse(**i) for i in items]

    async def create_timetable(self, user_id: str, req: TimetableCreate) -> TimetableResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        res = await self.repo.create_timetable(data)
        return TimetableResponse(**res)

    async def update_timetable(self, timetable_id: str, user_id: str, req: TimetableUpdate) -> TimetableResponse:
        data = req.model_dump(exclude_unset=True)
        res = await self.repo.update_timetable(timetable_id, user_id, data)
        if not res:
            raise NotFoundException("Timetable not found.", code="TIMETABLE_NOT_FOUND")
        return TimetableResponse(**res)

    async def delete_timetable(self, timetable_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete_timetable(timetable_id, user_id)
        if not deleted:
            raise NotFoundException("Timetable not found.", code="TIMETABLE_NOT_FOUND")
        return True

    # Conflict Detection
    async def detect_conflicts(
        self,
        user_id: str,
        timetable_id: str,
        day_of_week: int,
        start_time_str: str,
        end_time_str: str,
        exclude_item_id: Optional[str] = None,
    ) -> ConflictCheckResult:
        """
        Detects time-range overlaps on the same day_of_week:
        existing.start < new.end AND existing.end > new.start
        """
        new_start = parse_time(start_time_str)
        new_end = parse_time(end_time_str)

        items = await self.repo.list_schedule_items(user_id, timetable_id=timetable_id, day_of_week=day_of_week)
        conflicts = []

        for ex in items:
            if exclude_item_id and str(ex["id"]) == str(exclude_item_id):
                continue

            ex_start = parse_time(ex["start_time"])
            ex_end = parse_time(ex["end_time"])

            if check_time_conflict(ex_start, ex_end, new_start, new_end):
                conflicts.append(ConflictItem(
                    conflicting_item_id=str(ex["id"]),
                    conflicting_title=ex.get("title", "Untitled Class"),
                    start_time=ex["start_time"],
                    end_time=ex["end_time"],
                    message=f"Conflicts with '{ex.get('title')}' ({ex['start_time']} - {ex['end_time']})",
                ))

        return ConflictCheckResult(
            has_conflict=len(conflicts) > 0,
            conflicts=conflicts,
        )

    # Schedule Items
    async def get_schedule_item(self, item_id: str, user_id: str) -> ScheduleItemResponse:
        item = await self.repo.get_schedule_item(item_id, user_id)
        if not item:
            raise NotFoundException("Schedule item not found.", code="SCHEDULE_ITEM_NOT_FOUND")
        return ScheduleItemResponse(**item)

    async def list_schedule_items(
        self,
        user_id: str,
        timetable_id: Optional[str] = None,
        day_of_week: Optional[int] = None,
    ) -> List[ScheduleItemResponse]:
        items = await self.repo.list_schedule_items(user_id, timetable_id=timetable_id, day_of_week=day_of_week)
        return [ScheduleItemResponse(**i) for i in items]

    async def create_schedule_item(self, user_id: str, req: ScheduleItemCreate) -> ScheduleItemResponse:
        await self.get_timetable(req.timetable_id, user_id)  # Validate timetable ownership
        data = req.model_dump()
        data["user_id"] = user_id
        data["type"] = req.type.value if req.type else "CLASS"
        res = await self.repo.create_schedule_item(data)
        return ScheduleItemResponse(**res)

    async def update_schedule_item(self, item_id: str, user_id: str, req: ScheduleItemUpdate) -> ScheduleItemResponse:
        data = req.model_dump(exclude_unset=True)
        if "type" in data and data["type"]:
            data["type"] = req.type.value
        res = await self.repo.update_schedule_item(item_id, user_id, data)
        if not res:
            raise NotFoundException("Schedule item not found.", code="SCHEDULE_ITEM_NOT_FOUND")
        return ScheduleItemResponse(**res)

    async def delete_schedule_item(self, item_id: str, user_id: str, soft: bool = True) -> bool:
        deleted = await self.repo.delete_schedule_item(item_id, user_id, soft=soft)
        if not deleted:
            raise NotFoundException("Schedule item not found.", code="SCHEDULE_ITEM_NOT_FOUND")
        return True

    # Occurrences and Windowed Views
    async def get_occurrences(
        self,
        user_id: str,
        start_date_str: str,
        end_date_str: str,
        timetable_id: Optional[str] = None,
    ) -> List[ScheduleOccurrenceResponse]:
        start_d = date.fromisoformat(start_date_str)
        end_d = date.fromisoformat(end_date_str)

        if not timetable_id:
            active = await self.repo.get_active_timetable(user_id)
            if not active:
                return []
            timetable_id = str(active["id"])

        items = await self.repo.list_schedule_items(user_id, timetable_id=timetable_id)
        exceptions = await self.repo.list_exceptions_in_range(user_id, start_date_str, end_date_str)

        all_occurrences = []
        for it in items:
            occs = expand_schedule_item_occurrences(it, start_d, end_d, exceptions=exceptions)
            all_occurrences.extend([ScheduleOccurrenceResponse(**o) for o in occs])

        # Sort by date and start_time
        all_occurrences.sort(key=lambda o: (o.date, o.start_time))
        return all_occurrences

    # Schedule Exceptions
    async def create_exception(self, user_id: str, req: ScheduleExceptionCreate) -> ScheduleExceptionResponse:
        await self.get_schedule_item(req.schedule_item_id, user_id)  # Validate ownership
        data = req.model_dump()
        data["user_id"] = user_id
        data["exception_type"] = req.exception_type.value
        res = await self.repo.create_exception(data)
        return ScheduleExceptionResponse(**res)

    async def list_exceptions_for_item(self, schedule_item_id: str, user_id: str) -> List[ScheduleExceptionResponse]:
        await self.get_schedule_item(schedule_item_id, user_id)
        items = await self.repo.list_exceptions_for_item(schedule_item_id, user_id)
        return [ScheduleExceptionResponse(**i) for i in items]

    async def delete_exception(self, exception_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete_exception(exception_id, user_id)
        if not deleted:
            raise NotFoundException("Schedule exception not found.", code="EXCEPTION_NOT_FOUND")
        return True


timetable_service = TimetableService()
