"""
Personal Events Repository
"""

from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class EventRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("events", has_soft_delete=False)

    async def get_by_id(self, event_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(event_id, user_id)

    async def list_events(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        sort_by: str = "start_at",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        items, total = await self.repo.list_all(
            user_id=user_id,
            sort_by=sort_by,
            ascending=ascending,
            page=1,
            page_size=1000,
        )
        if start_date or end_date:
            filtered = []
            for ev in items:
                ev_start = str(ev.get("start_at", ""))
                if start_date and ev_start < start_date:
                    continue
                if end_date and ev_start > end_date:
                    continue
                filtered.append(ev)
            items = filtered
            total = len(items)

        start = (page - 1) * page_size
        return items[start : start + page_size], total

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(data)

    async def update(self, event_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(event_id, user_id, data)

    async def delete(self, event_id: str, user_id: str) -> bool:
        return await self.repo.delete(event_id, user_id, soft=False)
