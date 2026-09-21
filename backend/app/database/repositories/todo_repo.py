"""
Todo, List, Subtask, and Tag Repositories
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.database.repositories.base import BaseRepository, InMemoryRepository


class TodoListRepository:
    def __init__(self, repo: Optional[BaseRepository] = None):
        self.repo = repo or InMemoryRepository("todo_lists", has_soft_delete=True)

    async def get_by_id(self, list_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        return await self.repo.get_by_id(list_id, user_id)

    async def list_for_user(self, user_id: str, include_archived: bool = False) -> List[Dict[str, Any]]:
        items, _ = await self.repo.list_all(
            user_id=user_id,
            filters=None if include_archived else {"is_archived": False},
            sort_by="sort_order",
            ascending=True,
            page=1,
            page_size=500,
        )
        return items

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.repo.create(data)

    async def update(self, list_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.repo.update(list_id, user_id, data)

    async def delete(self, list_id: str, user_id: str, soft: bool = True) -> bool:
        return await self.repo.delete(list_id, user_id, soft=soft)


class TodoRepository:
    def __init__(
        self,
        todo_repo: Optional[BaseRepository] = None,
        subtask_repo: Optional[BaseRepository] = None,
        tag_repo: Optional[BaseRepository] = None,
    ):
        self.repo = todo_repo or InMemoryRepository("todos", has_soft_delete=True)
        self.subtask_repo = subtask_repo or InMemoryRepository("subtasks", has_soft_delete=False)
        self.tag_repo = tag_repo or InMemoryRepository("tags", has_soft_delete=False)
        # In-memory mapping for todo_id -> set of tag_ids
        self._todo_tags: Dict[str, List[str]] = {}

    async def get_by_id(self, todo_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        todo = await self.repo.get_by_id(todo_id, user_id)
        if not todo:
            return None
        # Attach subtasks
        subtasks, _ = await self.subtask_repo.list_all(
            user_id=user_id,
            filters={"todo_id": todo_id},
            sort_by="sort_order",
            ascending=True,
            page=1,
            page_size=100,
        )
        todo["subtasks"] = subtasks
        # Attach tags
        tag_ids = self._todo_tags.get(todo_id, [])
        tags = []
        for tid in tag_ids:
            t = await self.tag_repo.get_by_id(tid, user_id)
            if t:
                tags.append(t)
        todo["tags"] = tags
        return todo

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
    ) -> Tuple[List[Dict[str, Any]], int]:
        filters: Dict[str, Any] = {}
        if list_id:
            filters["list_id"] = list_id
        if project_id:
            filters["project_id"] = project_id
        if status:
            filters["status"] = status
        if priority:
            filters["priority"] = priority

        items, total = await self.repo.list_all(
            user_id=user_id,
            filters=filters,
            sort_by=sort_by,
            ascending=ascending,
            page=page,
            page_size=page_size,
        )

        # Filter by search query if present
        if search_query:
            q = search_query.lower()
            items = [item for item in items if q in item.get("title", "").lower() or q in (item.get("description") or "").lower()]
            total = len(items)

        # Populate subtasks and tags for each
        for item in items:
            item_id = str(item["id"])
            subtasks, _ = await self.subtask_repo.list_all(
                user_id=user_id,
                filters={"todo_id": item_id},
                sort_by="sort_order",
                ascending=True,
                page=1,
                page_size=100,
            )
            item["subtasks"] = subtasks
            tag_ids = self._todo_tags.get(item_id, [])
            item["tags"] = [await self.tag_repo.get_by_id(t_id, user_id) for t_id in tag_ids if await self.tag_repo.get_by_id(t_id, user_id)]

        return items, total

    async def create(self, data: Dict[str, Any], tag_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        created = await self.repo.create(data)
        todo_id = str(created["id"])
        if tag_ids:
            self._todo_tags[todo_id] = list(tag_ids)
        created["subtasks"] = []
        created["tags"] = []
        return created

    async def update(self, todo_id: str, user_id: str, data: Dict[str, Any], tag_ids: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        updated = await self.repo.update(todo_id, user_id, data)
        if not updated:
            return None
        if tag_ids is not None:
            self._todo_tags[todo_id] = list(tag_ids)
        return await self.get_by_id(todo_id, user_id)

    async def delete(self, todo_id: str, user_id: str, soft: bool = True) -> bool:
        return await self.repo.delete(todo_id, user_id, soft=soft)

    # Subtask operations
    async def create_subtask(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.subtask_repo.create(data)

    async def update_subtask(self, subtask_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        return await self.subtask_repo.update(subtask_id, user_id, data)

    async def delete_subtask(self, subtask_id: str, user_id: str) -> bool:
        return await self.subtask_repo.delete(subtask_id, user_id, soft=False)

    # Tag operations
    async def list_tags(self, user_id: str) -> List[Dict[str, Any]]:
        items, _ = await self.tag_repo.list_all(user_id=user_id, sort_by="name", ascending=True, page=1, page_size=200)
        return items

    async def create_tag(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return await self.tag_repo.create(data)

    async def delete_tag(self, tag_id: str, user_id: str) -> bool:
        return await self.tag_repo.delete(tag_id, user_id, soft=False)
