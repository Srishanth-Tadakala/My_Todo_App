"""
Notifications and Expo Devices Router
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from app.core.idempotency import idempotency_cache
from app.core.responses import success_response
from app.dependencies import get_current_user_id, get_idempotency_key
from app.schemas.common import PaginatedResponse
from app.schemas.notification import DeviceRegisterRequest, DeviceResponse, NotificationLogResponse
from app.services.notification_service import notification_service
from app.utils.pagination import build_paginated_response

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("/devices", response_model=DeviceResponse, status_code=201)
async def register_device(
    req: DeviceRegisterRequest,
    idempotency_key: Optional[str] = Depends(get_idempotency_key),
    user_id: str = Depends(get_current_user_id),
):
    """
    Registers or updates an Expo push notification token for the user's mobile device.
    Supports multiple devices per user (iOS, Android, Web).
    """
    if idempotency_key:
        cached = idempotency_cache.get(f"device:{user_id}:{idempotency_key}")
        if cached:
            return cached[1]

    created = await notification_service.register_device(user_id, req)

    if idempotency_key:
        idempotency_cache.set(f"device:{user_id}:{idempotency_key}", 201, created)

    return created


@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(user_id: str = Depends(get_current_user_id)):
    """Lists active notification devices for the user."""
    return await notification_service.list_devices(user_id)


@router.delete("/devices/{device_id}", status_code=200)
async def remove_device(device_id: str, user_id: str = Depends(get_current_user_id)):
    """Deletes or deactivates an Expo push token on logout."""
    await notification_service.delete_device(device_id, user_id)
    return success_response({"message": "Device unregistered successfully."})


@router.get("/logs", response_model=PaginatedResponse[NotificationLogResponse])
async def list_notification_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
):
    """Returns historical notification logs for the user with delivery status."""
    items, total = await notification_service.list_logs(user_id, page=page, page_size=page_size)
    return build_paginated_response(items, total, page, page_size)


@router.post("/test", status_code=200)
async def send_test_notification(
    title: str = Query("Test Notification"),
    body: str = Query("This is a test notification from the Advanced Todo backend!"),
    user_id: str = Depends(get_current_user_id),
):
    """Sends an immediate test push notification to all user devices."""
    dispatched = await notification_service.dispatch_notification(
        user_id=user_id,
        entity_type="EVENT",
        entity_id="test-notification",
        reminder_id=None,
        notification_type="TEST",
        title=title,
        body=body,
    )
    return success_response({"dispatched": dispatched, "message": "Test notification executed."})
