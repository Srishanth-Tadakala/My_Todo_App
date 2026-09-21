"""
Reminders and Quiet Hours Tests
"""

from datetime import datetime, timezone
import pytest
from app.utils.datetime import adjust_for_quiet_hours, parse_datetime


@pytest.mark.asyncio
async def test_reminder_crud(client, auth_headers):
    # Create Reminder
    future_time = "2026-10-15T15:00:00Z"
    payload = {
        "entity_type": "TODO",
        "entity_id": "00000000-0000-0000-0000-000000000010",
        "reminder_type": "DUE_SOON",
        "remind_at": future_time,
        "channel": "PUSH",
    }
    res = await client.post("/api/v1/reminders", json=payload, headers=auth_headers)
    assert res.status_code == 201
    rem_id = res.json()["id"]
    assert res.json()["status"] == "PENDING"

    # List Reminders
    list_res = await client.get("/api/v1/reminders", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # Cancel Reminder
    del_res = await client.delete(f"/api/v1/reminders/{rem_id}", headers=auth_headers)
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_quiet_hours_adjustment(client, auth_headers):
    # Enable quiet hours: 22:00:00 to 07:00:00 (UTC)
    await client.put(
        "/api/v1/users/settings",
        json={
            "quiet_hours_enabled": True,
            "quiet_hours_start": "22:00:00",
            "quiet_hours_end": "07:00:00",
            "timezone": "UTC",
        },
        headers=auth_headers,
    )

    # 1. Daytime reminder (14:00) -> should NOT be adjusted
    day_time = "2026-10-15T14:00:00Z"
    res_day = await client.post(
        "/api/v1/reminders",
        json={
            "entity_type": "TODO",
            "entity_id": "00000000-0000-0000-0000-000000000011",
            "remind_at": day_time,
        },
        headers=auth_headers,
    )
    assert res_day.status_code == 201
    assert "14:00:00" in res_day.json()["remind_at"]

    # 2. Nighttime reminder (03:00) -> should be shifted to 07:00:00
    night_time = "2026-10-15T03:00:00Z"
    res_night = await client.post(
        "/api/v1/reminders",
        json={
            "entity_type": "TODO",
            "entity_id": "00000000-0000-0000-0000-000000000012",
            "remind_at": night_time,
        },
        headers=auth_headers,
    )
    assert res_night.status_code == 201
    # Check that time was shifted to 07:00:00
    assert "07:00:00" in res_night.json()["remind_at"]
