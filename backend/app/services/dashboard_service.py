"""
Dashboard Service
Aggregates key home screen metrics in a single API call for Expo.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List
from app.database.repositories import assignment_repo, exam_repo, hackathon_repo, todo_repo
from app.schemas.dashboard import DashboardResponse, DashboardTodayStats, DeadlineItem
from app.services.timetable_service import timetable_service
from app.utils.datetime import now_utc, parse_datetime


class DashboardService:
    def __init__(self, t_repo=None, tt_service=None, a_repo=None, e_repo=None, h_repo=None):
        self.todo_repo = t_repo or todo_repo
        self.timetable_service = tt_service or timetable_service
        self.assignment_repo = a_repo or assignment_repo
        self.exam_repo = e_repo or exam_repo
        self.hackathon_repo = h_repo or hackathon_repo

    async def get_dashboard(self, user_id: str) -> DashboardResponse:
        now = now_utc()
        today_str = now.date().isoformat()
        seven_days_later_str = (now.date() + timedelta(days=7)).isoformat()

        # 1. Todos metrics & Overdue
        todos, _ = await self.todo_repo.list_todos(user_id=user_id, page_size=500)
        completed_today = 0
        pending_today = 0
        overdue_tasks = []

        for t in todos:
            status = t.get("status")
            due_at_str = t.get("due_at")

            if status == "COMPLETED":
                comp_at = t.get("completed_at")
                if comp_at and str(comp_at)[:10] == today_str:
                    completed_today += 1
            else:
                # Pending
                if due_at_str:
                    dt = parse_datetime(due_at_str)
                    if dt < now:
                        overdue_tasks.append(t)
                    elif str(due_at_str)[:10] == today_str:
                        pending_today += 1

        today_stats = DashboardTodayStats(
            completed=completed_today,
            pending=pending_today,
            overdue=len(overdue_tasks),
        )

        # 2. Today's Schedule & Next Schedule Item
        today_occurrences = await self.timetable_service.get_occurrences(
            user_id=user_id,
            start_date_str=today_str,
            end_date_str=today_str,
        )
        today_schedule = [o.model_dump() for o in today_occurrences]

        # Find next schedule item
        now_time_str = now.strftime("%H:%M:%S")
        next_item = None
        for item in today_schedule:
            if item.get("start_time", "") > now_time_str:
                next_item = item
                break

        # 3. Upcoming Deadlines (Next 7 days across Todos, Assignments, Exams, Hackathons)
        deadlines: List[DeadlineItem] = []

        # From Todos
        for t in todos:
            if t.get("status") != "COMPLETED" and t.get("due_at"):
                due_date_str = str(t["due_at"])[:10]
                if today_str <= due_date_str <= seven_days_later_str:
                    deadlines.append(DeadlineItem(
                        id=str(t["id"]),
                        entity_type="TODO",
                        title=t["title"],
                        due_at=str(t["due_at"]),
                        priority=t.get("priority"),
                        status=t.get("status"),
                    ))

        # From Assignments
        assignments, _ = await self.assignment_repo.list_assignments(user_id=user_id, page_size=100)
        for a in assignments:
            if a.get("status") not in ("COMPLETED", "SUBMITTED") and a.get("due_at"):
                due_date_str = str(a["due_at"])[:10]
                if today_str <= due_date_str <= seven_days_later_str:
                    deadlines.append(DeadlineItem(
                        id=str(a["id"]),
                        entity_type="ASSIGNMENT",
                        title=a["title"],
                        due_at=str(a["due_at"]),
                        priority=a.get("priority"),
                        status=a.get("status"),
                    ))

        # From Exams
        exams, _ = await self.exam_repo.list_exams(user_id=user_id, page_size=100)
        for e in exams:
            if e.get("exam_date") and today_str <= str(e["exam_date"]) <= seven_days_later_str:
                deadlines.append(DeadlineItem(
                    id=str(e["id"]),
                    entity_type="EXAM",
                    title=e["title"],
                    due_at=f"{e['exam_date']}T{e.get('start_time', '09:00:00')}Z",
                    priority="URGENT",
                    status="UPCOMING",
                ))

        # Sort deadlines by due_at
        deadlines.sort(key=lambda d: d.due_at)

        return DashboardResponse(
            today=today_stats,
            next_schedule=next_item,
            upcoming_deadlines=deadlines[:10],
            overdue_tasks=overdue_tasks[:10],
            today_schedule=today_schedule,
        )


dashboard_service = DashboardService()
