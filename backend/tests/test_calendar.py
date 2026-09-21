"""
Unified Calendar Tests
"""

import pytest


@pytest.mark.asyncio
async def test_unified_calendar(client, auth_headers):
    # 1. Create a Todo
    await client.post(
        "/api/v1/todos",
        json={"title": "Submit Project Report", "due_at": "2026-09-10T12:00:00Z"},
        headers=auth_headers,
    )

    # 2. Create an Assignment
    await client.post(
        "/api/v1/assignments",
        json={"title": "Math Problem Set 4", "due_at": "2026-09-12T18:00:00Z"},
        headers=auth_headers,
    )

    # 3. Create an Event
    await client.post(
        "/api/v1/events",
        json={"title": "Department Orientation", "start_at": "2026-09-15T09:00:00Z", "end_at": "2026-09-15T11:00:00Z"},
        headers=auth_headers,
    )

    # 4. Query Unified Calendar for September 2026
    res = await client.get("/api/v1/calendar?start=2026-09-01&end=2026-09-30", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    # Verify todos, assignments, events populated
    assert len(data["todos"]) == 1
    assert data["todos"][0]["title"] == "Submit Project Report"

    assert len(data["assignments"]) == 1
    assert data["assignments"][0]["title"] == "Math Problem Set 4"

    assert len(data["events"]) == 1
    assert data["events"][0]["title"] == "Department Orientation"

    # Verify query for October returns 0 of these items
    oct_res = await client.get("/api/v1/calendar?start=2026-10-01&end=2026-10-31", headers=auth_headers)
    assert oct_res.status_code == 200
    oct_data = oct_res.json()
    assert len(oct_data["todos"]) == 0
    assert len(oct_data["assignments"]) == 0
    assert len(oct_data["events"]) == 0
