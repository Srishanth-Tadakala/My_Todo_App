"""
Users Router (Profiles and Settings)
"""

from fastapi import APIRouter, Depends
from app.dependencies import get_current_user_id
from app.schemas.user import ProfileResponse, ProfileUpdate, UserSettingsResponse, UserSettingsUpdate
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user_id)):
    """Retrieves user profile."""
    return await user_service.get_profile(user_id)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(req: ProfileUpdate, user_id: str = Depends(get_current_user_id)):
    """Updates user profile information."""
    return await user_service.update_profile(user_id, req)


@router.get("/settings", response_model=UserSettingsResponse)
async def get_settings(user_id: str = Depends(get_current_user_id)):
    """Retrieves user settings including quiet hours and notification preferences."""
    return await user_service.get_settings(user_id)


@router.put("/settings", response_model=UserSettingsResponse)
async def update_settings(req: UserSettingsUpdate, user_id: str = Depends(get_current_user_id)):
    """Updates user preferences and quiet hours."""
    return await user_service.update_settings(user_id, req)
