"""
User and Settings Repository
"""

from typing import Any, Dict, Optional
from app.database.repositories.base import BaseRepository, InMemoryRepository, SupabasePostgrestRepository


class UserRepository:
    """Manages profiles and user settings."""

    def __init__(self, backend_repo: Optional[BaseRepository] = None, settings_repo: Optional[BaseRepository] = None):
        self.profile_repo = backend_repo or InMemoryRepository("profiles", has_soft_delete=False)
        self.settings_repo = settings_repo or InMemoryRepository("user_settings", has_soft_delete=False)

    async def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        # In profiles, primary key id IS user_id
        return await self.profile_repo.get_by_id(user_id, user_id)

    async def update_profile(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        existing = await self.get_profile(user_id)
        if not existing:
            data_to_create = dict(data)
            data_to_create["id"] = user_id
            return await self.profile_repo.create(data_to_create)
        return await self.profile_repo.update(user_id, user_id, data)

    async def get_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        # In user_settings, user_id is the primary key
        res = await self.settings_repo.get_by_id(user_id, user_id)
        if not res:
            # Default settings
            default_data = {
                "id": user_id,
                "user_id": user_id,
                "default_reminder_minutes": 30,
                "quiet_hours_enabled": False,
                "quiet_hours_start": "22:00:00",
                "quiet_hours_end": "07:00:00",
                "timezone": "UTC",
                "daily_summary_enabled": True,
                "daily_summary_time": "08:00:00",
                "weekly_summary_enabled": True,
                "sound_enabled": True,
                "vibration_enabled": True,
            }
            return await self.settings_repo.create(default_data)
        return res

    async def update_settings(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        existing = await self.get_settings(user_id)
        return await self.settings_repo.update(user_id, user_id, data)
