"""
Notifications, Devices, and Attachments Repositories
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class DeviceRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("devices", has_soft_delete=False)

    async def get_by_id(self, device_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(device_id, user_id)

    async def list_active_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        items, _ = await self.repo.list_all(
            user_id=user_id,
            filters={"is_active": True},
            page=1,
            page_size=50,
        )
        return items

    async def register_device(
        self,
        user_id: str,
        expo_push_token: str,
        platform: str,
        device_name: Optional[str] = None,
    ) -> Dict[str, Any]:
        # Check if already registered
        items, _ = await self.repo.list_all(user_id=user_id, page=1, page_size=100)
        for d in items:
            if d.get("expo_push_token") == expo_push_token:
                # Update existing
                return await self.repo.update(
                    str(d["id"]),
                    user_id,
                    {"platform": platform, "device_name": device_name, "is_active": True},
                )

        # Create new
        return await self.repo.create({
            "user_id": user_id,
            "expo_push_token": expo_push_token,
            "platform": platform,
            "device_name": device_name,
            "is_active": True,
        })

    async def deactivate_token(self, expo_push_token: str) -> bool:
        """Deactivates device when Expo reports DeviceNotRegistered."""
        if isinstance(self.repo, InMemoryRepository):
            for item in self.repo._items.values():
                if item.get("expo_push_token") == expo_push_token:
                    item["is_active"] = False
                    item["updated_at"] = datetime.now(timezone.utc).isoformat()
                    return True
        return False

    async def delete(self, device_id: str, user_id: str) -> bool:
        return await self.repo.delete(device_id, user_id, soft=False)


class NotificationLogRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("notification_logs", has_soft_delete=False)
        # In-memory tracking of unique key (user_id, entity_type, entity_id, reminder_id, notification_type)
        self._unique_keys: set = set()

    async def has_duplicate(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        reminder_id: Optional[str],
        notification_type: str,
    ) -> bool:
        key = (str(user_id), entity_type, str(entity_id), str(reminder_id or ""), notification_type)
        return key in self._unique_keys

    async def create_log(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        reminder_id: Optional[str],
        notification_type: str,
        title: str,
        body: str,
        channel: str = "PUSH",
        status: str = "SENT",
        error_message: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        key = (str(user_id), entity_type, str(entity_id), str(reminder_id or ""), notification_type)
        if key in self._unique_keys:
            # Atomic deduplication triggered
            return None

        log_data = {
            "user_id": user_id,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "reminder_id": reminder_id,
            "notification_type": notification_type,
            "title": title,
            "body": body,
            "channel": channel,
            "status": status,
            "error_message": error_message,
        }
        res = await self.repo.create(log_data)
        self._unique_keys.add(key)
        return res

    async def list_for_user(self, user_id: str, page: int = 1, page_size: int = 50) -> Tuple[List[Dict[str, Any]], int]:
        return await self.repo.list_all(
            user_id=user_id,
            sort_by="created_at",
            ascending=False,
            page=page,
            page_size=page_size,
        )


class AttachmentRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("attachments", has_soft_delete=False)

    async def get_by_id(self, attachment_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(attachment_id, user_id)

    async def list_for_entity(self, user_id: str, entity_type: str, entity_id: str) -> List[Dict[str, Any]]:
        items, _ = await self.repo.list_all(
            user_id=user_id,
            filters={"entity_type": entity_type, "entity_id": entity_id},
            sort_by="created_at",
            ascending=False,
            page=1,
            page_size=100,
        )
        return items

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(data)

    async def delete(self, attachment_id: str, user_id: str) -> bool:
        return await self.repo.delete(attachment_id, user_id, soft=False)
