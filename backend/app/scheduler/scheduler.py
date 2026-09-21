"""
APScheduler Instance and Lifespan Management
Runs single-instance periodic workers within the FastAPI process.
"""

from typing import Optional
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.config import get_settings
from app.core.logging import logger
from app.scheduler.jobs import check_overdue_todos, process_due_reminders

_scheduler: Optional[AsyncIOScheduler] = None


def get_scheduler() -> AsyncIOScheduler:
    """Returns singleton AsyncIOScheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = AsyncIOScheduler()
    return _scheduler


def start_scheduler():
    """Initializes and starts the periodic scheduler."""
    settings = get_settings()
    sched = get_scheduler()

    # Register reminder job
    sched.add_job(
        process_due_reminders,
        "interval",
        seconds=settings.REMINDER_CHECK_INTERVAL_SECONDS,
        id="process_due_reminders",
        replace_existing=True,
    )

    # Register overdue todos check
    sched.add_job(
        check_overdue_todos,
        "interval",
        seconds=settings.OVERDUE_CHECK_INTERVAL_SECONDS,
        id="check_overdue_todos",
        replace_existing=True,
    )

    if not sched.running:
        sched.start()
        logger.info("APScheduler started successfully.")


def stop_scheduler():
    """Gracefully shuts down the scheduler."""
    sched = get_scheduler()
    if sched.running:
        sched.shutdown(wait=False)
        logger.info("APScheduler stopped.")
