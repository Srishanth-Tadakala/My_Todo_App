"""
Base Repository Interface and Implementations
Provides unified data access with automatic user-id scoping and soft-deletion support.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar
import uuid

T = TypeVar("T")


class BaseRepository(ABC):
    """Abstract Base Repository for user-owned entities."""

    @abstractmethod
    async def get_by_id(self, entity_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve single entity by ID scoped to user."""
        pass

    @abstractmethod
    async def list_all(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = "created_at",
        ascending: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """List entities with filtering, sorting, pagination, and user isolation."""
        pass

    @abstractmethod
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new entity."""
        pass

    @abstractmethod
    async def update(self, entity_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update entity scoped to user."""
        pass

    @abstractmethod
    async def delete(self, entity_id: str, user_id: str, soft: bool = True) -> bool:
        """Delete entity (soft or hard delete) scoped to user."""
        pass


class InMemoryRepository(BaseRepository):
    """
    In-Memory Repository Implementation.
    Used for offline testing and development without live database dependencies.
    """

    def __init__(self, table_name: str, has_soft_delete: bool = True):
        self.table_name = table_name
        self.has_soft_delete = has_soft_delete
        self._items: Dict[str, Dict[str, Any]] = {}

    async def get_by_id(self, entity_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        item = self._items.get(str(entity_id))
        if not item:
            return None
        if item.get("user_id") != str(user_id) and item.get("id") != str(user_id):
            return None
        if self.has_soft_delete and item.get("deleted_at") is not None:
            return None
        return dict(item)

    async def list_all(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = "created_at",
        ascending: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        matched = []
        user_str = str(user_id) if user_id else None

        for item in self._items.values():
            if user_str and item.get("user_id") != user_str:
                continue
            if self.has_soft_delete and item.get("deleted_at") is not None:
                continue

            # Apply filters
            match = True
            if filters:
                for k, v in filters.items():
                    if v is not None and item.get(k) != v:
                        match = False
                        break
            if match:
                matched.append(dict(item))

        # Sort
        if sort_by:
            matched.sort(
                key=lambda x: str(x.get(sort_by) or ""),
                reverse=not ascending,
            )

        total = len(matched)
        start = (page - 1) * page_size
        end = start + page_size
        return matched[start:end], total

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        item = dict(data)
        if "id" not in item:
            item["id"] = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()
        if "created_at" not in item:
            item["created_at"] = now
        item["updated_at"] = now
        self._items[str(item["id"])] = item
        return dict(item)

    async def update(self, entity_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = await self.get_by_id(entity_id, user_id)
        if not existing:
            return None

        updated = dict(existing)
        for k, v in data.items():
            if k not in ("id", "user_id", "created_at"):
                updated[k] = v

        updated["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._items[str(entity_id)] = updated
        return dict(updated)

    async def delete(self, entity_id: str, user_id: str, soft: bool = True) -> bool:
        existing = await self.get_by_id(entity_id, user_id)
        if not existing:
            return False

        if soft and self.has_soft_delete:
            self._items[str(entity_id)]["deleted_at"] = datetime.now(timezone.utc).isoformat()
        else:
            self._items.pop(str(entity_id), None)
        return True


class SupabasePostgrestRepository(BaseRepository):
    """
    Production Supabase PostgREST repository implementation.
    Enforces user_id scoping on every single operation.
    """

    def __init__(self, table_name: str, client, has_soft_delete: bool = True):
        self.table_name = table_name
        self.client = client
        self.has_soft_delete = has_soft_delete

    async def get_by_id(self, entity_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        query = self.client.table(self.table_name).select("*").eq("id", entity_id)
        # For profiles, primary key is user_id
        if self.table_name != "profiles":
            query = query.eq("user_id", user_id)
        if self.has_soft_delete:
            query = query.is_("deleted_at", "null")

        res = query.execute()
        return res.data[0] if res.data else None

    async def list_all(
        self,
        user_id: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = "created_at",
        ascending: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = self.client.table(self.table_name).select("*", count="exact").eq("user_id", user_id)
        if self.has_soft_delete:
            query = query.is_("deleted_at", "null")

        if filters:
            for k, v in filters.items():
                if v is not None:
                    query = query.eq(k, v)

        if sort_by:
            query = query.order(sort_by, desc=not ascending)

        start = (page - 1) * page_size
        end = start + page_size - 1
        query = query.range(start, end)

        res = query.execute()
        total = res.count or len(res.data)
        return res.data, total

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        res = self.client.table(self.table_name).insert(data).execute()
        if not res.data:
            raise RuntimeError(f"Failed to insert into {self.table_name}")
        return res.data[0]

    async def update(self, entity_id: str, user_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = self.client.table(self.table_name).update(data).eq("id", entity_id)
        if self.table_name != "profiles":
            query = query.eq("user_id", user_id)
        if self.has_soft_delete:
            query = query.is_("deleted_at", "null")

        res = query.execute()
        return res.data[0] if res.data else None

    async def delete(self, entity_id: str, user_id: str, soft: bool = True) -> bool:
        if soft and self.has_soft_delete:
            now = datetime.now(timezone.utc).isoformat()
            res = (
                self.client.table(self.table_name)
                .update({"deleted_at": now})
                .eq("id", entity_id)
                .eq("user_id", user_id)
                .execute()
            )
            return bool(res.data)
        else:
            res = (
                self.client.table(self.table_name)
                .delete()
                .eq("id", entity_id)
                .eq("user_id", user_id)
                .execute()
            )
            return bool(res.data)
