"""
Assignment Service
"""

from typing import List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import assignment_repo
from app.schemas.assignment import AssignmentCreate, AssignmentResponse, AssignmentUpdate
from app.schemas.reminder import EntityType, ReminderType
from app.services.reminder_service import reminder_service
from app.utils.datetime import parse_datetime


class AssignmentService:
    def __init__(self, a_repo=None, r_service=None):
        self.repo = a_repo or assignment_repo
        self.reminder_service = r_service or reminder_service

    async def get_assignment(self, assignment_id: str, user_id: str) -> AssignmentResponse:
        item = await self.repo.get_by_id(assignment_id, user_id)
        if not item:
            raise NotFoundException("Assignment not found.", code="ASSIGNMENT_NOT_FOUND")
        return AssignmentResponse(**item)

    async def list_assignments(
        self,
        user_id: str,
        subject_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        sort_by: str = "due_at",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[AssignmentResponse], int]:
        items, total = await self.repo.list_assignments(
            user_id=user_id,
            subject_id=subject_id,
            status=status,
            priority=priority,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        return [AssignmentResponse(**i) for i in items], total

    async def create_assignment(self, user_id: str, req: AssignmentCreate) -> AssignmentResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        data["status"] = req.status.value if req.status else "NOT_STARTED"
        data["priority"] = req.priority.value if req.priority else "MEDIUM"
        res = await self.repo.create(data)
        assign_id = str(res["id"])

        # Schedule reminder 24h before due_at
        due_dt = parse_datetime(req.due_at)
        await self.reminder_service.schedule_entity_reminder(
            user_id=user_id,
            entity_type=EntityType.ASSIGNMENT,
            entity_id=assign_id,
            target_time_utc=due_dt,
            minutes_before=1440,  # 24 hours
            reminder_type=ReminderType.DEADLINE_APPROACHING,
        )

        return AssignmentResponse(**res)

    async def update_assignment(self, assignment_id: str, user_id: str, req: AssignmentUpdate) -> AssignmentResponse:
        data = req.model_dump(exclude_unset=True)
        if "status" in data and data["status"]:
            data["status"] = req.status.value
            if data["status"] in ("SUBMITTED", "COMPLETED"):
                await self.reminder_service.cancel_for_entity(user_id, EntityType.ASSIGNMENT.value, assignment_id)
        if "priority" in data and data["priority"]:
            data["priority"] = req.priority.value

        res = await self.repo.update(assignment_id, user_id, data)
        if not res:
            raise NotFoundException("Assignment not found.", code="ASSIGNMENT_NOT_FOUND")

        # Update reminder if due_at changed
        if "due_at" in data and data["due_at"]:
            due_dt = parse_datetime(data["due_at"])
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.ASSIGNMENT,
                entity_id=assignment_id,
                target_time_utc=due_dt,
                minutes_before=1440,
                reminder_type=ReminderType.DEADLINE_APPROACHING,
            )

        return AssignmentResponse(**res)

    async def delete_assignment(self, assignment_id: str, user_id: str) -> bool:
        deleted = await self.repo.delete(assignment_id, user_id)
        if not deleted:
            raise NotFoundException("Assignment not found.", code="ASSIGNMENT_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.ASSIGNMENT.value, assignment_id)
        return True


assignment_service = AssignmentService()
