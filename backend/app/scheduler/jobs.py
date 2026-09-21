"""
Background Scheduler Jobs
Periodic workers for reminder processing and overdue task detection.
"""

from datetime import datetime, timedelta, timezone
from typing import Dict
from app.core.logging import logger
from app.database.repositories import reminder_repo, todo_repo
from app.services.notification_service import notification_service
from app.utils.datetime import now_utc, parse_datetime

# Exponential backoff in minutes for retries: attempt 1 -> 2m, attempt 2 -> 10m
RETRY_DELAYS_MINUTES = [2, 10]


def format_notification_text(entity_type: str, reminder_type: str, entity_title: str) -> tuple[str, str]:
    """Generates user-friendly title and body for the notification."""
    title_prefix = {
        "TODO": "Todo Reminder",
        "SCHEDULE": "Class / Schedule",
        "ASSIGNMENT": "Assignment Deadline",
        "EXAM": "Exam Alert",
        "HACKATHON": "Hackathon Deadline",
        "CERTIFICATION": "Certification Alert",
        "INTERNSHIP": "Internship Update",
        "EVENT": "Upcoming Event",
    }.get(entity_type, "Reminder")

    if reminder_type == "DUE_NOW":
        return f"{title_prefix}: Due Now", f"'{entity_title}' is due right now!"
    elif reminder_type == "CLASS_STARTING":
        return f"{title_prefix}: Starting Soon", f"Your class '{entity_title}' starts shortly."
    elif reminder_type == "DEADLINE_APPROACHING":
        return f"{title_prefix}: Approaching", f"Upcoming deadline for '{entity_title}'."
    elif reminder_type == "CERTIFICATION_EXPIRING":
        return f"{title_prefix}: Expiring Soon", f"Your certification '{entity_title}' is nearing expiration."
    elif reminder_type == "INTERVIEW_UPCOMING":
        return f"{title_prefix}: Interview Soon", f"Interview scheduled for '{entity_title}'."
    elif reminder_type == "EVENT_STARTING":
        return f"{title_prefix}: Event Starting", f"Event '{entity_title}' begins soon."
    elif reminder_type == "OVERDUE":
        return f"{title_prefix}: Overdue", f"'{entity_title}' is overdue. Consider rescheduling."
    else:
        return f"{title_prefix}", f"Reminder for '{entity_title}'."


async def process_due_reminders(cutoff: Optional[datetime] = None):
    """
    Periodic job: Polls for due reminders and dispatches notifications.
    Ensures strict user-scoping, exponential retry, and deduplication.
    """
    cutoff_time = cutoff or now_utc()
    due_reminders = await reminder_repo.list_due_reminders(cutoff_time)
    if not due_reminders:
        return

    logger.info(f"Processing {len(due_reminders)} due reminder(s)...")

    for rem in due_reminders:
        rem_id = str(rem["id"])
        user_id = str(rem["user_id"])
        entity_type = rem["entity_type"]
        entity_id = str(rem["entity_id"])
        rem_type = rem.get("reminder_type", "DUE_SOON")
        attempt_count = rem.get("attempt_count", 0) + 1

        # Mark PROCESSING
        await reminder_repo.update_status(rem_id, status="PROCESSING", attempt_count=attempt_count)

        # Generate notification text
        title, body = format_notification_text(entity_type, rem_type, entity_title=f"{entity_type} Item")

        # Dispatch via NotificationService
        success = await notification_service.dispatch_notification(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            reminder_id=rem_id,
            notification_type=rem_type,
            title=title,
            body=body,
            channel=rem.get("channel", "PUSH"),
        )

        if success:
            await reminder_repo.update_status(rem_id, status="SENT")
            logger.info(f"Reminder {rem_id} sent successfully.")
        else:
            # Handle retry
            if attempt_count <= len(RETRY_DELAYS_MINUTES):
                delay_min = RETRY_DELAYS_MINUTES[attempt_count - 1]
                next_retry = now_utc() + timedelta(minutes=delay_min)
                await reminder_repo.update_status(
                    rem_id,
                    status="FAILED",
                    attempt_count=attempt_count,
                    error_message="Dispatch failed, queued for retry.",
                    next_retry_at=next_retry,
                )
                logger.warning(f"Reminder {rem_id} failed. Retrying in {delay_min} minutes.")
            else:
                await reminder_repo.update_status(
                    rem_id,
                    status="FAILED",
                    attempt_count=attempt_count,
                    error_message="Max retry attempts exceeded.",
                )
                logger.error(f"Reminder {rem_id} permanently failed.")


async def check_overdue_todos():
    """
    Periodic job: Scans for overdue todos and tasks frequently postponed.
    Generates rescheduling prompts where postponed_count >= 3.
    """
    now = now_utc()
    # In memory or DB check
    # Check all active todos
    all_todos, _ = await todo_repo.list_todos(user_id="", page_size=1000)
    # The scheduler runs with service-role context across all todos
    for t in all_todos:
        status = t.get("status")
        if status in ("COMPLETED", "CANCELLED"):
            continue

        user_id = str(t["user_id"])
        todo_id = str(t["id"])
        due_at = t.get("due_at")
        postponed = t.get("postponed_count", 0)

        # 1. Frequently postponed notification
        if postponed >= 3:
            await notification_service.dispatch_notification(
                user_id=user_id,
                entity_type="TODO",
                entity_id=todo_id,
                reminder_id=None,
                notification_type="POSTPONE_PROMPT",
                title="Reschedule Suggestion",
                body=f"You've postponed '{t['title']}' several times. Would you like to reschedule it?",
                channel="IN_APP",
            )

        # 2. Overdue notification
        if due_at and parse_datetime(due_at) < now:
            await notification_service.dispatch_notification(
                user_id=user_id,
                entity_type="TODO",
                entity_id=todo_id,
                reminder_id=None,
                notification_type="OVERDUE",
                title="Task Overdue",
                body=f"Task '{t['title']}' is overdue.",
                channel="IN_APP",
            )
