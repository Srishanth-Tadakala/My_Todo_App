"""
Todo List Schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class TodoListCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default="list", max_length=50)
    color: Optional[str] = Field(default="#3B82F6", max_length=20)
    sort_order: Optional[int] = Field(default=0, ge=0)


class TodoListUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    icon: Optional[str] = Field(default=None, max_length=50)
    color: Optional[str] = Field(default=None, max_length=20)
    sort_order: Optional[int] = Field(default=None, ge=0)
    is_archived: Optional[bool] = None


class TodoListStats(BaseModel):
    total_todos: int = 0
    completed_todos: int = 0
    pending_todos: int = 0
    completion_rate: float = 0.0


class TodoListResponse(BaseModel):
    id: str
    user_id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    is_archived: bool = False
    stats: Optional[TodoListStats] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
