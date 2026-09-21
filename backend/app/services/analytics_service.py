"""
Productivity Analytics Service
"""

from datetime import datetime, timedelta, timezone
from app.database.repositories import todo_repo
from app.schemas.analytics import AnalyticsSummaryResponse
from app.utils.datetime import now_utc, parse_datetime


class AnalyticsService:
    def __init__(self, t_repo=None):
        self.todo_repo = t_repo or todo_repo

    async def get_summary(self, user_id: str, period: str = "today") -> AnalyticsSummaryResponse:
        now = now_utc()
        today_date = now.date()

        if period == "today":
            start_date = today_date
        elif period == "this_week":
            start_date = today_date - timedelta(days=today_date.weekday())
        elif period == "this_month":
            start_date = today_date.replace(day=1)
        else:
            period = "today"
            start_date = today_date

        start_iso = start_date.isoformat()

        todos, _ = await self.todo_repo.list_todos(user_id=user_id, page_size=1000)

        created = 0
        completed = 0
        pending = 0
        overdue = 0
        postponed = 0

        for t in todos:
            created_at = str(t.get("created_at", ""))[:10]
            if created_at >= start_iso:
                created += 1

            status = t.get("status")
            if status == "COMPLETED":
                completed += 1
            else:
                pending += 1
                due_at = t.get("due_at")
                if due_at and parse_datetime(due_at) < now:
                    overdue += 1

            postponed += t.get("postponed_count", 0)

        total_tracked = completed + pending
        rate = (completed / total_tracked * 100.0) if total_tracked > 0 else 0.0

        return AnalyticsSummaryResponse(
            period=period,
            tasks_created=created,
            tasks_completed=completed,
            tasks_pending=pending,
            tasks_overdue=overdue,
            tasks_postponed=postponed,
            completion_rate=round(rate, 1),
        )


analytics_service = AnalyticsService()
