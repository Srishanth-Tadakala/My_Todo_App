"""
Subjects, Timetables, Schedule Items, and Exceptions Repository
"""

from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class SubjectRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("subjects", has_soft_delete=False)

    async def get_by_id(self, subject_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(subject_id, user_id)

    async def list_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        items, _ = await self.repo.list_all(user_id=user_id, sort_by="name", ascending=True, page=1, page_size=200)
        return items

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(data)

    async def update(self, subject_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(subject_id, user_id, data)

    async def delete(self, subject_id: str, user_id: str) -> bool:
        return await self.repo.delete(subject_id, user_id, soft=False)


class TimetableRepository:
    def __init__(
        self,
        timetable_repo: Optional[BaseRepository] = None,
        item_repo: Optional[BaseRepository] = None,
        exception_repo: Optional[BaseRepository] = None,
    ):
        self.timetable_repo = timetable_repo or InMemoryRepository("timetables", has_soft_delete=False)
        self.item_repo = item_repo or InMemoryRepository("schedule_items", has_soft_delete=True)
        self.exception_repo = exception_repo or InMemoryRepository("schedule_exceptions", has_soft_delete=False)

    async def get_timetable(self, timetable_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.timetable_repo.get_by_id(timetable_id, user_id)

    async def get_active_timetable(self, user_id: str) -> Optional[Dict[str, Any]]:
        items, _ = await self.timetable_repo.list_all(
            user_id=user_id,
            filters={"is_active": True},
            page=1,
            page_size=1,
        )
        return items[0] if items else None

    async def list_timetables(self, user_id: str) -> List[Dict[str, Any]]:
        items, _ = await self.timetable_repo.list_all(user_id=user_id, sort_by="created_at", ascending=False, page=1, page_size=50)
        return items

    async def create_timetable(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.timetable_repo.create(data)

    async def update_timetable(self, timetable_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.timetable_repo.update(timetable_id, user_id, data)

    async def delete_timetable(self, timetable_id: str, user_id: str) -> bool:
        return await self.timetable_repo.delete(timetable_id, user_id, soft=False)

    # Schedule Items
    async def get_schedule_item(self, item_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.item_repo.get_by_id(item_id, user_id)

    async def list_schedule_items(
        self,
        user_id: str,
        timetable_id: Optional[str] = None,
        day_of_week: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        filters: Dict[str, Any] = {}
        if timetable_id:
            filters["timetable_id"] = timetable_id
        if day_of_week is not None:
            filters["day_of_week"] = day_of_week

        items, _ = await self.item_repo.list_all(
            user_id=user_id,
            filters=filters,
            sort_by="start_time",
            ascending=True,
            page=1,
            page_size=500,
        )
        return items

    async def create_schedule_item(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.item_repo.create(data)

    async def update_schedule_item(self, item_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.item_repo.update(item_id, user_id, data)

    async def delete_schedule_item(self, item_id: str, user_id: str, soft: bool = True) -> bool:
        return await self.item_repo.delete(item_id, user_id, soft=soft)

    # Schedule Exceptions
    async def get_exception(self, exception_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.exception_repo.get_by_id(exception_id, user_id)

    async def list_exceptions_for_item(self, schedule_item_id: str, user_id: str) -> List[Dict[str, Any]]:
        items, _ = await self.exception_repo.list_all(
            user_id=user_id,
            filters={"schedule_item_id": schedule_item_id},
            sort_by="date",
            ascending=True,
            page=1,
            page_size=100,
        )
        return items

    async def list_exceptions_in_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict[str, Any]]:
        items, _ = await self.exception_repo.list_all(user_id=user_id, page=1, page_size=1000)
        return [ex for ex in items if start_date <= str(ex.get("date")) <= end_date]

    async def create_exception(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.exception_repo.create(data)

    async def delete_exception(self, exception_id: str, user_id: str) -> bool:
        return await self.exception_repo.delete(exception_id, user_id, soft=False)
