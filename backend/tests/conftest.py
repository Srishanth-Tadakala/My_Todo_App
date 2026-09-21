"""
Pytest Fixtures and Global Configuration
"""

import os
import pytest
import httpx
from httpx import ASGITransport
from app.config import get_settings
from app.database import repositories as repos
from app.database.repositories.base import InMemoryRepository
from app.main import app

# Set testing environment
os.environ["APP_ENV"] = "testing"
get_settings().APP_ENV = "testing"


@pytest.fixture(autouse=True)
def reset_in_memory_databases():
    """Resets all in-memory repository dictionaries before each test."""
    for repo_obj in [
        repos.user_repo.profile_repo,
        repos.user_repo.settings_repo,
        repos.todo_list_repo.repo,
        repos.todo_repo.repo,
        repos.todo_repo.subtask_repo,
        repos.todo_repo.tag_repo,
        repos.subject_repo.repo,
        repos.timetable_repo.timetable_repo,
        repos.timetable_repo.item_repo,
        repos.timetable_repo.exception_repo,
        repos.assignment_repo.repo,
        repos.exam_repo.repo,
        repos.hackathon_repo.repo,
        repos.cert_repo.repo,
        repos.internship_repo.repo,
        repos.project_repo.repo,
        repos.event_repo.repo,
        repos.reminder_repo.repo,
        repos.device_repo.repo,
        repos.notification_log_repo.repo,
        repos.attachment_repo.repo,
    ]:
        if isinstance(repo_obj, InMemoryRepository):
            repo_obj._items.clear()

    repos.todo_repo._todo_tags.clear()
    repos.notification_log_repo._unique_keys.clear()


@pytest.fixture
async def client():
    """Async HTTP test client for FastAPI application."""
    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c


@pytest.fixture
def auth_headers():
    """Authorization headers for primary test user."""
    return {"Authorization": "Bearer test-token-00000000-0000-0000-0000-000000000001"}


@pytest.fixture
def auth_headers_user2():
    """Authorization headers for secondary user (for isolation / tenant tests)."""
    return {"Authorization": "Bearer test-token-00000000-0000-0000-0000-000000000002"}
