"""
Reminders Repository
Handles concrete reminders and scheduler polling.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class ReminderRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("reminders", has_soft_delete=False)

    async def get_by_id(self, reminder_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(reminder_id, user_id)

    async def list_for_user(
        self,
        user_id: str,
        status: Optional[str] = None,
        entity_type: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
    ) -> Tuple[List[Dict[str, Any]], int]:
        filters: Dict[str, Any] = {}
        if status:
            filters["status"] = status
        if entity_type:
            filters["entity_type"] = entity_type

        return await self.repo.list_all(
            user_id=user_id,
            filters=filters,
            sort_by="remind_at",
            ascending=True,
            page=page,
            page_size=page_size,
        )

    async def list_due_reminders(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """
        Scheduler method to retrieve all pending reminders due for dispatch.
        Can also pick up retries where status='FAILED' and next_retry_at <= cutoff_time and attempt_count < 3.
        """
        cutoff_iso = cutoff_time.isoformat()
        due_items = []
        
        # When in memory
        if isinstance(self.repo, InMemoryRepository):
            for item in self.repo._items.values():
                status = item.get("status")
                remind_at = item.get("remind_at")
                attempt_count = item.get("attempt_count", 0)
                next_retry = item.get("next_retry_at")

                if status == "PENDING" and remind_at and str(remind_at) <= cutoff_iso:
                    due_items.append(dict(item))
                elif status == "FAILED" and attempt_count < 3 and next_retry and str(next_retry) <= cutoff_iso:
                    due_items.append(dict(item))
        return due_items

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(data)

    async def update(self, reminder_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(reminder_id, user_id, data)

    async def update_status(
        self,
        reminder_id: str,
        status: str,
        attempt_count: Optional[int] = None,
        error_message: Optional[str] = None,
        next_retry_at: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """Used by background scheduler to update execution results."""
        if isinstance(self.repo, InMemoryRepository):
            item = self.repo._items.get(str(reminder_id))
            if not item:
                return None
            item["status"] = status
            item["last_attempt_at"] = datetime.now(timezone.utc).isoformat()
            if attempt_count is not None:
                item["attempt_count"] = attempt_count
            if error_message is not None:
                item["error_message"] = error_message
            if next_retry_at is not None:
                item["next_retry_at"] = next_retry_at.isoformat()
            item["updated_at"] = datetime.now(timezone.utc).isoformat()
            return dict(item)
        return None

    async def cancel_for_entity(self, user_id: str, entity_type: str, entity_id: str) -> int:
        """Cancels any pending reminders when an entity is completed or deleted."""
        cancelled = 0
        if isinstance(self.repo, InMemoryRepository):
            for item in list(self.repo._items.values()):
                if (
                    item.get("user_id") == str(user_id)
                    and item.get("entity_type") == entity_type
                    and item.get("entity_id") == str(entity_id)
                    and item.get("status") in ("PENDING", "FAILED")
                ):
                    item["status"] = "CANCELLED"
                    item["updated_at"] = datetime.now(timezone.utc).isoformat()
                    cancelled += 1
        return cancelled
