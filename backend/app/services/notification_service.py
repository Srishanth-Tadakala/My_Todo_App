"""
Notification and Expo Push Dispatch Service
Handles device tokens, push dispatch, deduplication, and dead token cleanup.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import httpx
from app.config import get_settings
from app.core.exceptions import NotFoundException
from app.core.logging import logger
from app.database.repositories import device_repo, notification_log_repo
from app.schemas.notification import DeviceRegisterRequest, DeviceResponse, NotificationLogResponse

EXPO_PUSH_URL = "https://exp.host/--/api/v2/push/send"


class NotificationService:
    def __init__(self, d_repo=None, n_repo=None):
        self.device_repo = d_repo or device_repo
        self.log_repo = n_repo or notification_log_repo

    # Device Management
    async def register_device(self, user_id: str, req: DeviceRegisterRequest) -> DeviceResponse:
        res = await self.device_repo.register_device(
            user_id=user_id,
            expo_push_token=req.expo_push_token,
            platform=req.platform,
            device_name=req.device_name,
        )
        return DeviceResponse(**res)

    async def list_devices(self, user_id: str) -> List[DeviceResponse]:
        items = await self.device_repo.list_active_for_user(user_id)
        return [DeviceResponse(**i) for i in items]

    async def delete_device(self, device_id: str, user_id: str) -> bool:
        deleted = await self.device_repo.delete(device_id, user_id)
        if not deleted:
            raise NotFoundException("Device not found.", code="DEVICE_NOT_FOUND")
        return True

    # Notification Dispatch
    async def dispatch_notification(
        self,
        user_id: str,
        entity_type: str,
        entity_id: str,
        reminder_id: Optional[str],
        notification_type: str,
        title: str,
        body: str,
        channel: str = "PUSH",
    ) -> bool:
        """
        Dispatches notification to all active devices of the user.
        Ensures strict deduplication via DB constraint / unique tracker.
        """
        # 1. Check duplicate
        if await self.log_repo.has_duplicate(user_id, entity_type, entity_id, reminder_id, notification_type):
            logger.info(f"Duplicate notification suppressed for user {user_id}, entity {entity_id}")
            return False

        # 2. Retrieve active devices
        devices = await self.device_repo.list_active_for_user(user_id)

        # 3. Create initial log to lock the unique constraint
        log_entry = await self.log_repo.create_log(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_id=reminder_id,
            notification_type=notification_type,
            title=title,
            body=body,
            channel=channel,
            status="SENT" if not devices else "PROCESSING",
        )

        if not log_entry:
            # Race condition caught by deduplication
            return False

        if not devices:
            logger.info(f"No active push devices found for user {user_id}. Logged as in-app notification.")
            return True

        # 4. Dispatch to Expo
        settings = get_settings()
        messages = []
        for dev in devices:
            messages.append({
                "to": dev["expo_push_token"],
                "sound": "default",
                "title": title,
                "body": body,
                "data": {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "notification_type": notification_type,
                },
            })

        headers = {
            "Accept": "application/json",
            "Accept-encoding": "gzip, deflate",
            "Content-Type": "application/json",
        }
        if settings.EXPO_ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {settings.EXPO_ACCESS_TOKEN}"

        # If testing or mock mode, skip real HTTP network call
        if settings.is_testing or "dummy" in settings.SUPABASE_ANON_KEY:
            logger.info(f"[TEST MOCK] Dispatched Expo Push notification: {title} - {body}")
            return True

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.post(EXPO_PUSH_URL, json=messages, headers=headers)
                if res.status_code == 200:
                    resp_data = res.json().get("data", [])
                    # Check for ticket errors (e.g. DeviceNotRegistered)
                    for idx, ticket in enumerate(resp_data):
                        if ticket.get("status") == "error":
                            err_code = ticket.get("details", {}).get("error")
                            if err_code == "DeviceNotRegistered":
                                dead_token = messages[idx]["to"]
                                logger.warning(f"Deactivating dead Expo token: {dead_token}")
                                await self.device_repo.deactivate_token(dead_token)
                    return True
                else:
                    logger.error(f"Expo push server returned HTTP {res.status_code}: {res.text}")
                    return False
        except Exception as e:
            logger.error(f"Error dispatching push to Expo: {e}")
            return False

    async def list_logs(self, user_id: str, page: int = 1, page_size: int = 50) -> Tuple[List[NotificationLogResponse], int]:
        items, total = await self.log_repo.list_for_user(user_id, page=page, page_size=page_size)
        return [NotificationLogResponse(**i) for i in items], total


notification_service = NotificationService()
