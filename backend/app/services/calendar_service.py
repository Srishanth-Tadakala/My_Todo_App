"""
Calendar Aggregation Service
Aggregates tasks, classes, deadlines, and events across a specified date range.
"""

from typing import Any, Dict, List
from app.database.repositories import (
    assignment_repo, cert_repo, event_repo, exam_repo, hackathon_repo, internship_repo, todo_repo
)
from app.schemas.calendar import CalendarResponse
from app.services.timetable_service import timetable_service


class CalendarService:
    def __init__(
        self,
        t_repo=None,
        tt_service=None,
        a_repo=None,
        e_repo=None,
        h_repo=None,
        c_repo=None,
        i_repo=None,
        ev_repo=None,
    ):
        self.todo_repo = t_repo or todo_repo
        self.timetable_service = tt_service or timetable_service
        self.assignment_repo = a_repo or assignment_repo
        self.exam_repo = e_repo or exam_repo
        self.hackathon_repo = h_repo or hackathon_repo
        self.cert_repo = c_repo or cert_repo
        self.internship_repo = i_repo or internship_repo
        self.event_repo = ev_repo or event_repo

    async def get_calendar(self, user_id: str, start_date: str, end_date: str) -> CalendarResponse:
        # 1. Todos
        todos, _ = await self.todo_repo.list_todos(user_id=user_id, page_size=500)
        filtered_todos = [
            t for t in todos
            if t.get("due_at") and start_date <= str(t["due_at"])[:10] <= end_date
        ]

        # 2. Classes (Expanded recurring occurrences with exceptions applied)
        classes = await self.timetable_service.get_occurrences(
            user_id=user_id,
            start_date_str=start_date,
            end_date_str=end_date,
        )

        # 3. Assignments
        assignments, _ = await self.assignment_repo.list_assignments(user_id=user_id, page_size=500)
        filtered_assignments = [
            a for a in assignments
            if a.get("due_at") and start_date <= str(a["due_at"])[:10] <= end_date
        ]

        # 4. Exams
        exams, _ = await self.exam_repo.list_exams(user_id=user_id, page_size=500)
        filtered_exams = [
            e for e in exams
            if e.get("exam_date") and start_date <= str(e["exam_date"]) <= end_date
        ]

        # 5. Hackathons
        hackathons, _ = await self.hackathon_repo.list_hackathons(user_id=user_id, page_size=500)
        filtered_hackathons = [
            h for h in hackathons
            if h.get("submission_deadline") and start_date <= str(h["submission_deadline"])[:10] <= end_date
        ]

        # 6. Certifications
        certs, _ = await self.cert_repo.list_certifications(user_id=user_id, page_size=500)
        filtered_certs = [
            c for c in certs
            if c.get("exam_date") and start_date <= str(c["exam_date"])[:10] <= end_date
        ]

        # 7. Internships
        internships, _ = await self.internship_repo.list_internships(user_id=user_id, page_size=500)
        filtered_internships = [
            i for i in internships
            if i.get("application_deadline") and start_date <= str(i["application_deadline"])[:10] <= end_date
        ]

        # 8. Events
        events, _ = await self.event_repo.list_events(user_id=user_id, start_date=start_date, end_date=end_date, page_size=500)

        return CalendarResponse(
            todos=filtered_todos,
            classes=[c.model_dump() for c in classes],
            assignments=filtered_assignments,
            exams=filtered_exams,
            hackathons=filtered_hackathons,
            certifications=filtered_certs,
            internships=filtered_internships,
            events=events,
        )


calendar_service = CalendarService()
