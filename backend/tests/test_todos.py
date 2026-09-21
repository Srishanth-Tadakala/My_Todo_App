"""
Todos, Lists, and Subtasks Tests
"""

from datetime import datetime, timedelta, timezone
import pytest


@pytest.mark.asyncio
async def test_create_and_get_todo_list(client, auth_headers):
    # Create list
    list_payload = {
        "name": "Academics",
        "description": "College related todos",
        "icon": "school",
        "color": "#3B82F6",
    }
    res = await client.post("/api/v1/lists", json=list_payload, headers=auth_headers)
    assert res.status_code == 201
    list_data = res.json()
    assert list_data["name"] == "Academics"
    list_id = list_data["id"]

    # Get list
    res_get = await client.get(f"/api/v1/lists/{list_id}", headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["id"] == list_id


@pytest.mark.asyncio
async def test_todo_crud_and_completion(client, auth_headers):
    # Create todo
    future_due = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()
    todo_payload = {
        "title": "Finish Assignment 1",
        "description": "DBMS indexing questions",
        "status": "TODO",
        "priority": "HIGH",
        "due_at": future_due,
        "estimated_minutes": 120,
    }
    res = await client.post("/api/v1/todos", json=todo_payload, headers=auth_headers)
    assert res.status_code == 201
    todo = res.json()
    assert todo["title"] == "Finish Assignment 1"
    assert todo["status"] == "TODO"
    assert todo["is_overdue"] is False
    todo_id = todo["id"]

    # Update todo
    update_res = await client.put(
        f"/api/v1/todos/{todo_id}",
        json={"title": "Finish Assignment 1 (Revised)", "priority": "URGENT"},
        headers=auth_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Finish Assignment 1 (Revised)"
    assert update_res.json()["priority"] == "URGENT"

    # Complete todo
    complete_res = await client.post(f"/api/v1/todos/{todo_id}/complete", headers=auth_headers)
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "COMPLETED"
    assert complete_res.json()["completed_at"] is not None

    # Reopen todo
    reopen_res = await client.post(f"/api/v1/todos/{todo_id}/reopen", headers=auth_headers)
    assert reopen_res.status_code == 200
    assert reopen_res.json()["status"] == "TODO"

    # Delete todo
    del_res = await client.delete(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert del_res.status_code == 200

    # Ensure deleted
    get_res = await client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert get_res.status_code == 404


@pytest.mark.asyncio
async def test_todo_postpone_and_prompt(client, auth_headers):
    todo_payload = {
        "title": "Study Algorithm Proofs",
        "status": "TODO",
        "due_at": datetime.now(timezone.utc).isoformat(),
    }
    res = await client.post("/api/v1/todos", json=todo_payload, headers=auth_headers)
    assert res.status_code == 201
    todo_id = res.json()["id"]

    # Postpone 3 times
    for i in range(1, 4):
        p_res = await client.post(f"/api/v1/todos/{todo_id}/postpone?minutes=60", headers=auth_headers)
        assert p_res.status_code == 200
        assert p_res.json()["postponed_count"] == i

    # Verify 3rd postponement flags needs_reschedule_prompt
    data = p_res.json()
    assert data["postponed_count"] == 3
    assert data["needs_reschedule_prompt"] is True


@pytest.mark.asyncio
async def test_subtasks_and_progress(client, auth_headers):
    # Create todo
    todo_res = await client.post(
        "/api/v1/todos",
        json={"title": "Software Project Milestone 1"},
        headers=auth_headers,
    )
    todo_id = todo_res.json()["id"]

    # Add 2 subtasks
    s1 = await client.post(
        f"/api/v1/todos/{todo_id}/subtasks",
        json={"title": "Design Database Schema", "sort_order": 1},
        headers=auth_headers,
    )
    s2 = await client.post(
        f"/api/v1/todos/{todo_id}/subtasks",
        json={"title": "Implement FastAPI Endpoints", "sort_order": 2},
        headers=auth_headers,
    )
    assert s1.status_code == 201
    assert s2.status_code == 201
    s1_id = s1.json()["id"]

    # Check progress (0/2 = 0%)
    check1 = await client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert check1.json()["subtask_progress"]["total"] == 2
    assert check1.json()["subtask_progress"]["completed"] == 0
    assert check1.json()["subtask_progress"]["percentage"] == 0.0

    # Complete 1 subtask
    await client.put(
        f"/api/v1/todos/subtasks/{s1_id}",
        json={"is_completed": True},
        headers=auth_headers,
    )

    # Check progress (1/2 = 50%)
    check2 = await client.get(f"/api/v1/todos/{todo_id}", headers=auth_headers)
    assert check2.json()["subtask_progress"]["completed"] == 1
    assert check2.json()["subtask_progress"]["percentage"] == 50.0
