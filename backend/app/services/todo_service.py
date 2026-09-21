"""
Todo Service
Handles Todos, Subtasks, Tags, Postponements, and Overdue tracking.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.core.exceptions import NotFoundException
from app.database.repositories import todo_repo, user_repo
from app.schemas.reminder import EntityType, ReminderType
from app.schemas.todo import (
    SubtaskCreate, SubtaskProgress, SubtaskResponse, SubtaskUpdate,
    TodoCreate, TodoPostpone, TodoReschedule, TodoResponse, TodoStatus, TodoUpdate
)
from app.schemas.tag import TagCreate, TagResponse
from app.services.reminder_service import reminder_service
from app.utils.datetime import now_utc, parse_datetime


class TodoService:
    def __init__(self, t_repo=None, u_repo=None, r_service=None):
        self.todo_repo = t_repo or todo_repo
        self.user_repo = u_repo or user_repo
        self.reminder_service = r_service or reminder_service

    def _enrich_todo(self, item: Dict[str, Any]) -> TodoResponse:
        subtasks = item.get("subtasks", [])
        total_subtasks = len(subtasks)
        completed_subtasks = sum(1 for s in subtasks if s.get("is_completed"))
        percentage = (completed_subtasks / total_subtasks * 100.0) if total_subtasks > 0 else 0.0

        progress = SubtaskProgress(
            total=total_subtasks,
            completed=completed_subtasks,
            percentage=round(percentage, 1),
        )

        # Check overdue status
        due_at_str = item.get("due_at")
        is_overdue = False
        if due_at_str and item.get("status") not in (TodoStatus.COMPLETED.value, TodoStatus.CANCELLED.value):
            dt = parse_datetime(due_at_str)
            if dt < now_utc():
                is_overdue = True

        postponed_count = item.get("postponed_count", 0)
        needs_prompt = postponed_count >= 3 and item.get("status") not in (TodoStatus.COMPLETED.value, TodoStatus.CANCELLED.value)

        return TodoResponse(
            id=str(item["id"]),
            user_id=str(item["user_id"]),
            list_id=item.get("list_id"),
            project_id=item.get("project_id"),
            title=item["title"],
            description=item.get("description"),
            status=item.get("status", "TODO"),
            priority=item.get("priority", "MEDIUM"),
            due_at=item.get("due_at"),
            timezone=item.get("timezone", "UTC"),
            estimated_minutes=item.get("estimated_minutes"),
            actual_minutes=item.get("actual_minutes"),
            reminder_enabled=item.get("reminder_enabled", False),
            completed_at=item.get("completed_at"),
            postponed_count=postponed_count,
            is_overdue=is_overdue,
            needs_reschedule_prompt=needs_prompt,
            subtask_progress=progress,
            subtasks=[SubtaskResponse(**s) for s in subtasks],
            tags=[TagResponse(**t) for t in item.get("tags", [])],
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
        )

    async def get_todo(self, todo_id: str, user_id: str) -> TodoResponse:
        item = await self.todo_repo.get_by_id(todo_id, user_id)
        if not item:
            raise NotFoundException("Todo not found.", code="TODO_NOT_FOUND")
        return self._enrich_todo(item)

    async def list_todos(
        self,
        user_id: str,
        list_id: Optional[str] = None,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        search_query: Optional[str] = None,
        sort_by: str = "due_at",
        ascending: bool = True,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[TodoResponse], int]:
        items, total = await self.todo_repo.list_todos(
            user_id=user_id,
            list_id=list_id,
            project_id=project_id,
            status=status,
            priority=priority,
            search_query=search_query,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )
        return [self._enrich_todo(i) for i in items], total

    async def create_todo(self, user_id: str, req: TodoCreate) -> TodoResponse:
        data = req.model_dump(exclude={"reminder_minutes_before", "tag_ids"})
        data["user_id"] = user_id
        data["status"] = req.status.value if req.status else "TODO"
        data["priority"] = req.priority.value if req.priority else "MEDIUM"
        data["postponed_count"] = 0

        created = await self.todo_repo.create(data, tag_ids=req.tag_ids)
        todo_id = str(created["id"])

        # Auto-schedule reminder if enabled and due_at is provided
        if req.reminder_enabled and req.due_at:
            due_dt = parse_datetime(req.due_at)
            minutes = req.reminder_minutes_before if req.reminder_minutes_before is not None else 30
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.TODO,
                entity_id=todo_id,
                target_time_utc=due_dt,
                minutes_before=minutes,
                reminder_type=ReminderType.DUE_SOON,
            )

        full = await self.todo_repo.get_by_id(todo_id, user_id)
        return self._enrich_todo(full)

    async def update_todo(self, todo_id: str, user_id: str, req: TodoUpdate) -> TodoResponse:
        existing = await self.todo_repo.get_by_id(todo_id, user_id)
        if not existing:
            raise NotFoundException("Todo not found.", code="TODO_NOT_FOUND")

        data = req.model_dump(exclude_unset=True, exclude={"tag_ids"})
        if "status" in data and data["status"]:
            data["status"] = req.status.value
            if req.status == TodoStatus.COMPLETED:
                data["completed_at"] = now_utc().isoformat()
                await self.reminder_service.cancel_for_entity(user_id, EntityType.TODO.value, todo_id)
            elif req.status in (TodoStatus.TODO, TodoStatus.IN_PROGRESS):
                data["completed_at"] = None

        if "priority" in data and data["priority"]:
            data["priority"] = req.priority.value

        updated = await self.todo_repo.update(todo_id, user_id, data, tag_ids=req.tag_ids)

        # Update reminder if due_at or reminder_enabled changed
        if updated.get("reminder_enabled") and updated.get("due_at"):
            due_dt = parse_datetime(updated["due_at"])
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.TODO,
                entity_id=todo_id,
                target_time_utc=due_dt,
                minutes_before=30,
                reminder_type=ReminderType.DUE_SOON,
            )
        elif not updated.get("reminder_enabled"):
            await self.reminder_service.cancel_for_entity(user_id, EntityType.TODO.value, todo_id)

        return self._enrich_todo(updated)

    async def complete_todo(self, todo_id: str, user_id: str) -> TodoResponse:
        return await self.update_todo(todo_id, user_id, TodoUpdate(status=TodoStatus.COMPLETED))

    async def reopen_todo(self, todo_id: str, user_id: str) -> TodoResponse:
        return await self.update_todo(todo_id, user_id, TodoUpdate(status=TodoStatus.TODO))

    async def cancel_todo(self, todo_id: str, user_id: str) -> TodoResponse:
        return await self.update_todo(todo_id, user_id, TodoUpdate(status=TodoStatus.CANCELLED))

    async def postpone_todo(self, todo_id: str, user_id: str, minutes: int = 1440) -> TodoResponse:
        existing = await self.todo_repo.get_by_id(todo_id, user_id)
        if not existing:
            raise NotFoundException("Todo not found.", code="TODO_NOT_FOUND")

        current_due = parse_datetime(existing.get("due_at") or now_utc())
        new_due = current_due + timedelta(minutes=minutes)
        postponed_count = existing.get("postponed_count", 0) + 1

        updated = await self.todo_repo.update(
            todo_id,
            user_id,
            {"due_at": new_due.isoformat(), "postponed_count": postponed_count},
        )

        if updated.get("reminder_enabled"):
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.TODO,
                entity_id=todo_id,
                target_time_utc=new_due,
                minutes_before=30,
                reminder_type=ReminderType.DUE_SOON,
            )

        return self._enrich_todo(updated)

    async def reschedule_todo(self, todo_id: str, user_id: str, req: TodoReschedule) -> TodoResponse:
        new_due_dt = parse_datetime(req.new_due_at)
        existing = await self.todo_repo.get_by_id(todo_id, user_id)
        if not existing:
            raise NotFoundException("Todo not found.", code="TODO_NOT_FOUND")

        updated = await self.todo_repo.update(
            todo_id,
            user_id,
            {"due_at": new_due_dt.isoformat()},
        )

        if updated.get("reminder_enabled"):
            await self.reminder_service.schedule_entity_reminder(
                user_id=user_id,
                entity_type=EntityType.TODO,
                entity_id=todo_id,
                target_time_utc=new_due_dt,
                minutes_before=30,
                reminder_type=ReminderType.DUE_SOON,
            )

        return self._enrich_todo(updated)

    async def delete_todo(self, todo_id: str, user_id: str, soft: bool = True) -> bool:
        deleted = await self.todo_repo.delete(todo_id, user_id, soft=soft)
        if not deleted:
            raise NotFoundException("Todo not found.", code="TODO_NOT_FOUND")
        await self.reminder_service.cancel_for_entity(user_id, EntityType.TODO.value, todo_id)
        return True

    # Subtasks
    async def create_subtask(self, todo_id: str, user_id: str, req: SubtaskCreate) -> SubtaskResponse:
        await self.get_todo(todo_id, user_id)  # Ensure exists and user owns
        data = req.model_dump()
        data["todo_id"] = todo_id
        data["user_id"] = user_id
        data["is_completed"] = False
        res = await self.todo_repo.create_subtask(data)
        return SubtaskResponse(**res)

    async def update_subtask(self, subtask_id: str, user_id: str, req: SubtaskUpdate) -> SubtaskResponse:
        data = req.model_dump(exclude_unset=True)
        if "is_completed" in data:
            data["completed_at"] = now_utc().isoformat() if data["is_completed"] else None
        res = await self.todo_repo.update_subtask(subtask_id, user_id, data)
        if not res:
            raise NotFoundException("Subtask not found.", code="SUBTASK_NOT_FOUND")
        return SubtaskResponse(**res)

    async def delete_subtask(self, subtask_id: str, user_id: str) -> bool:
        deleted = await self.todo_repo.delete_subtask(subtask_id, user_id)
        if not deleted:
            raise NotFoundException("Subtask not found.", code="SUBTASK_NOT_FOUND")
        return True

    # Tags
    async def list_tags(self, user_id: str) -> List[TagResponse]:
        items = await self.todo_repo.list_tags(user_id)
        return [TagResponse(**i) for i in items]

    async def create_tag(self, user_id: str, req: TagCreate) -> TagResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        res = await self.todo_repo.create_tag(data)
        return TagResponse(**res)

    async def delete_tag(self, tag_id: str, user_id: str) -> bool:
        deleted = await self.todo_repo.delete_tag(tag_id, user_id)
        if not deleted:
            raise NotFoundException("Tag not found.", code="TAG_NOT_FOUND")
        return True


todo_service = TodoService()
