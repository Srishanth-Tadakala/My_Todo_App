"""
User Profile and Settings Service
"""

from typing import Any, Dict, Optional
from app.core.exceptions import NotFoundException
from app.database.repositories import user_repo
from app.schemas.user import ProfileResponse, ProfileUpdate, UserSettingsResponse, UserSettingsUpdate


class UserService:
    def __init__(self, u_repo=None):
        self.user_repo = u_repo or user_repo

    async def get_profile(self, user_id: str) -> ProfileResponse:
        prof = await self.user_repo.get_profile(user_id)
        if not prof:
            # Create default profile if not present
            prof = await self.user_repo.update_profile(user_id, {"full_name": None, "timezone": "UTC"})
        return ProfileResponse(**prof)

    async def update_profile(self, user_id: str, req: ProfileUpdate) -> ProfileResponse:
        data = req.model_dump(exclude_unset=True)
        prof = await self.user_repo.update_profile(user_id, data)
        return ProfileResponse(**prof)

    async def get_settings(self, user_id: str) -> UserSettingsResponse:
        settings = await self.user_repo.get_settings(user_id)
        return UserSettingsResponse(**settings)

    async def update_settings(self, user_id: str, req: UserSettingsUpdate) -> UserSettingsResponse:
        data = req.model_dump(exclude_unset=True)
        updated = await self.user_repo.update_settings(user_id, data)
        return UserSettingsResponse(**updated)


user_service = UserService()
