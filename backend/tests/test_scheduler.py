"""
Scheduler Acceptance Tests (Timing, Deduplication, Retry, and Overdue Processing)
"""

from datetime import datetime, timezone
import pytest
from app.database.repositories import notification_log_repo, reminder_repo, todo_repo
from app.scheduler.jobs import check_overdue_todos, process_due_reminders


@pytest.mark.asyncio
async def test_scheduler_timing_and_deduplication():
    user_id = "00000000-0000-0000-0000-000000000001"
    target_time_str = "2026-10-15T10:00:00+00:00"

    # Create pending reminder scheduled for 10:00:00
    rem = await reminder_repo.create({
        "user_id": user_id,
        "entity_type": "TODO",
        "entity_id": "00000000-0000-0000-0000-000000000020",
        "reminder_type": "DUE_SOON",
        "remind_at": target_time_str,
        "channel": "PUSH",
        "status": "PENDING",
    })
    rem_id = str(rem["id"])

    # 1. Timeline check at 09:59:00 -> should NOT be picked up
    cutoff_before = datetime.fromisoformat("2026-10-15T09:59:00+00:00")
    due_items = await reminder_repo.list_due_reminders(cutoff_before)
    assert len(due_items) == 0

    # 2. Timeline check at 10:00:00 -> should be picked up and processed
    cutoff_exact = datetime.fromisoformat("2026-10-15T10:00:00+00:00")
    due_items = await reminder_repo.list_due_reminders(cutoff_exact)
    assert len(due_items) == 1
    assert str(due_items[0]["id"]) == rem_id

    # Execute scheduler job
    await process_due_reminders(cutoff=cutoff_exact)

    # Verify status changed to SENT
    rem_after = await reminder_repo.get_by_id(rem_id, user_id)
    assert rem_after["status"] == "SENT"

    # 3. Timeline check at 10:01:00 -> reminder is SENT, should NOT be re-dispatched
    cutoff_after = datetime.fromisoformat("2026-10-15T10:01:00+00:00")
    due_items_after = await reminder_repo.list_due_reminders(cutoff_after)
    assert len(due_items_after) == 0

    # Verify notification log recorded exactly 1 entry
    logs, count = await notification_log_repo.list_for_user(user_id)
    assert count == 1
    assert logs[0]["reminder_id"] == rem_id


@pytest.mark.asyncio
async def test_overdue_and_postponed_task_alerts():
    user_id = "00000000-0000-0000-0000-000000000001"

    # Create todo that has been postponed 3 times
    todo = await todo_repo.create({
        "user_id": user_id,
        "title": "Tax Filing Documents",
        "status": "TODO",
        "postponed_count": 3,
        "due_at": "2026-09-01T10:00:00+00:00",  # Overdue
    })

    # Run overdue checker job
    await check_overdue_todos()

    # Check that notification logs contain reschedule prompt
    logs, count = await notification_log_repo.list_for_user(user_id)
    assert count >= 1
    postpone_logs = [l for l in logs if l.get("notification_type") == "POSTPONE_PROMPT"]
    assert len(postpone_logs) == 1
    assert "Tax Filing Documents" in postpone_logs[0]["body"]
