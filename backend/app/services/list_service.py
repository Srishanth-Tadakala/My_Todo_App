"""
Todo List Service
"""

from typing import Any, Dict, List, Optional
from app.core.exceptions import NotFoundException
from app.database.repositories import todo_list_repo, todo_repo
from app.schemas.list import TodoListCreate, TodoListResponse, TodoListStats, TodoListUpdate


class TodoListService:
    def __init__(self, l_repo=None, t_repo=None):
        self.list_repo = l_repo or todo_list_repo
        self.todo_repo = t_repo or todo_repo

    async def get_list(self, list_id: str, user_id: str) -> TodoListResponse:
        item = await self.list_repo.get_by_id(list_id, user_id)
        if not item:
            raise NotFoundException("Todo list not found.", code="LIST_NOT_FOUND")
        stats = await self.get_list_stats(list_id, user_id)
        return TodoListResponse(**item, stats=stats)

    async def list_for_user(self, user_id: str, include_archived: bool = False) -> List[TodoListResponse]:
        items = await self.list_repo.list_for_user(user_id, include_archived)
        results = []
        for item in items:
            stats = await self.get_list_stats(str(item["id"]), user_id)
            results.append(TodoListResponse(**item, stats=stats))
        return results

    async def create_list(self, user_id: str, req: TodoListCreate) -> TodoListResponse:
        data = req.model_dump()
        data["user_id"] = user_id
        created = await self.list_repo.create(data)
        return TodoListResponse(**created, stats=TodoListStats())

    async def update_list(self, list_id: str, user_id: str, req: TodoListUpdate) -> TodoListResponse:
        data = req.model_dump(exclude_unset=True)
        updated = await self.list_repo.update(list_id, user_id, data)
        if not updated:
            raise NotFoundException("Todo list not found.", code="LIST_NOT_FOUND")
        stats = await self.get_list_stats(list_id, user_id)
        return TodoListResponse(**updated, stats=stats)

    async def archive_list(self, list_id: str, user_id: str) -> TodoListResponse:
        return await self.update_list(list_id, user_id, TodoListUpdate(is_archived=True))

    async def restore_list(self, list_id: str, user_id: str) -> TodoListResponse:
        return await self.update_list(list_id, user_id, TodoListUpdate(is_archived=False))

    async def delete_list(self, list_id: str, user_id: str) -> bool:
        deleted = await self.list_repo.delete(list_id, user_id, soft=True)
        if not deleted:
            raise NotFoundException("Todo list not found.", code="LIST_NOT_FOUND")
        return True

    async def reorder_lists(self, user_id: str, ordered_ids: List[str]) -> List[TodoListResponse]:
        for idx, l_id in enumerate(ordered_ids):
            await self.list_repo.update(l_id, user_id, {"sort_order": idx})
        return await self.list_for_user(user_id, include_archived=True)

    async def get_list_stats(self, list_id: str, user_id: str) -> TodoListStats:
        todos, _ = await self.todo_repo.list_todos(user_id=user_id, list_id=list_id, page_size=1000)
        total = len(todos)
        completed = sum(1 for t in todos if t.get("status") == "COMPLETED")
        pending = total - completed
        rate = (completed / total * 100.0) if total > 0 else 0.0
        return TodoListStats(
            total_todos=total,
            completed_todos=completed,
            pending_todos=pending,
            completion_rate=round(rate, 1),
        )


todo_list_service = TodoListService()
