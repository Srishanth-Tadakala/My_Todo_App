"""
Unified Search Service
Performs fast ILIKE search across all user-owned domain models.
"""

from typing import List
from app.database.repositories import (
    assignment_repo, cert_repo, event_repo, exam_repo, hackathon_repo,
    internship_repo, project_repo, subject_repo, todo_repo
)
from app.schemas.search import SearchResponse, SearchResultItem


class SearchService:
    def __init__(
        self,
        t_repo=None,
        s_repo=None,
        a_repo=None,
        e_repo=None,
        h_repo=None,
        c_repo=None,
        i_repo=None,
        p_repo=None,
        ev_repo=None,
    ):
        self.todo_repo = t_repo or todo_repo
        self.subject_repo = s_repo or subject_repo
        self.assignment_repo = a_repo or assignment_repo
        self.exam_repo = e_repo or exam_repo
        self.hackathon_repo = h_repo or hackathon_repo
        self.cert_repo = c_repo or cert_repo
        self.internship_repo = i_repo or internship_repo
        self.project_repo = p_repo or project_repo
        self.event_repo = ev_repo or event_repo

    async def search_all(self, user_id: str, query: str) -> SearchResponse:
        q = query.strip().lower()
        if not q:
            return SearchResponse(query=query, total_results=0, results=[])

        results: List[SearchResultItem] = []

        # 1. Todos
        todos, _ = await self.todo_repo.list_todos(user_id=user_id, search_query=q, page_size=100)
        for t in todos:
            results.append(SearchResultItem(
                type="TODO",
                id=str(t["id"]),
                title=t["title"],
                description=t.get("description"),
                metadata={"status": t.get("status"), "priority": t.get("priority"), "due_at": t.get("due_at")},
            ))

        # 2. Subjects
        subjects = await self.subject_repo.list_for_user(user_id)
        for s in subjects:
            if q in s.get("name", "").lower() or q in (s.get("code") or "").lower() or q in (s.get("notes") or "").lower():
                results.append(SearchResultItem(
                    type="SUBJECT",
                    id=str(s["id"]),
                    title=f"{s.get('code', '')} - {s['name']}".strip(" -"),
                    description=s.get("notes"),
                    metadata={"teacher": s.get("teacher"), "semester": s.get("semester")},
                ))

        # 3. Assignments
        assignments, _ = await self.assignment_repo.list_assignments(user_id=user_id, page_size=100)
        for a in assignments:
            if q in a.get("title", "").lower() or q in (a.get("description") or "").lower():
                results.append(SearchResultItem(
                    type="ASSIGNMENT",
                    id=str(a["id"]),
                    title=a["title"],
                    description=a.get("description"),
                    metadata={"due_at": a.get("due_at"), "status": a.get("status")},
                ))

        # 4. Exams
        exams, _ = await self.exam_repo.list_exams(user_id=user_id, page_size=100)
        for e in exams:
            if q in e.get("title", "").lower() or q in (e.get("syllabus") or "").lower():
                results.append(SearchResultItem(
                    type="EXAM",
                    id=str(e["id"]),
                    title=e["title"],
                    description=e.get("syllabus"),
                    metadata={"exam_date": e.get("exam_date"), "room": e.get("room")},
                ))

        # 5. Hackathons
        hackathons, _ = await self.hackathon_repo.list_hackathons(user_id=user_id, page_size=100)
        for h in hackathons:
            if q in h.get("name", "").lower() or q in (h.get("organizer") or "").lower():
                results.append(SearchResultItem(
                    type="HACKATHON",
                    id=str(h["id"]),
                    title=h["name"],
                    description=f"Organizer: {h.get('organizer', 'N/A')}",
                    metadata={"status": h.get("status"), "deadline": h.get("submission_deadline")},
                ))

        # 6. Certifications
        certs, _ = await self.cert_repo.list_certifications(user_id=user_id, page_size=100)
        for c in certs:
            if q in c.get("name", "").lower() or q in (c.get("provider") or "").lower():
                results.append(SearchResultItem(
                    type="CERTIFICATION",
                    id=str(c["id"]),
                    title=c["name"],
                    description=f"Provider: {c.get('provider', 'N/A')}",
                    metadata={"status": c.get("status"), "exam_date": c.get("exam_date")},
                ))

        # 7. Internships
        internships, _ = await self.internship_repo.list_internships(user_id=user_id, page_size=100)
        for i in internships:
            if q in i.get("company", "").lower() or q in i.get("role", "").lower():
                results.append(SearchResultItem(
                    type="INTERNSHIP",
                    id=str(i["id"]),
                    title=f"{i['company']} - {i['role']}",
                    description=i.get("notes"),
                    metadata={"status": i.get("status"), "deadline": i.get("application_deadline")},
                ))

        # 8. Projects
        projects, _ = await self.project_repo.list_projects(user_id=user_id, page_size=100)
        for p in projects:
            if q in p.get("name", "").lower() or q in (p.get("description") or "").lower():
                results.append(SearchResultItem(
                    type="PROJECT",
                    id=str(p["id"]),
                    title=p["name"],
                    description=p.get("description"),
                    metadata={"status": p.get("status")},
                ))

        # 9. Events
        events, _ = await self.event_repo.list_events(user_id=user_id, page_size=100)
        for ev in events:
            if q in ev.get("title", "").lower() or q in (ev.get("description") or "").lower() or q in (ev.get("location") or "").lower():
                results.append(SearchResultItem(
                    type="EVENT",
                    id=str(ev["id"]),
                    title=ev["title"],
                    description=ev.get("description"),
                    metadata={"start_at": ev.get("start_at"), "location": ev.get("location")},
                ))

        return SearchResponse(query=query, total_results=len(results), results=results)


search_service = SearchService()
