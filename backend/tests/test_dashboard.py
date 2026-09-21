"""
Dashboard Home Screen API Tests
"""

from datetime import datetime, timedelta, timezone
import pytest


@pytest.mark.asyncio
async def test_dashboard_aggregation(client, auth_headers):
    now = datetime.now(timezone.utc)
    today_due = (now + timedelta(hours=3)).isoformat()
    overdue_due = (now - timedelta(days=2)).isoformat()

    # 1. Pending todo due today
    await client.post(
        "/api/v1/todos",
        json={"title": "Prepare Presentation", "due_at": today_due, "status": "TODO"},
        headers=auth_headers,
    )

    # 2. Overdue todo
    await client.post(
        "/api/v1/todos",
        json={"title": "Submit Lab Report", "due_at": overdue_due, "status": "TODO"},
        headers=auth_headers,
    )

    # 3. Completed todo today
    t3 = await client.post(
        "/api/v1/todos",
        json={"title": "Morning Reading", "due_at": today_due},
        headers=auth_headers,
    )
    await client.post(f"/api/v1/todos/{t3.json()['id']}/complete", headers=auth_headers)

    # 4. Fetch Dashboard
    dash_res = await client.get("/api/v1/dashboard", headers=auth_headers)
    assert dash_res.status_code == 200
    dash = dash_res.json()

    # Verify today counters
    assert dash["today"]["pending"] >= 1
    assert dash["today"]["overdue"] >= 1
    assert dash["today"]["completed"] >= 1

    # Verify overdue tasks array contains the overdue task
    overdue_titles = [t["title"] for t in dash["overdue_tasks"]]
    assert "Submit Lab Report" in overdue_titles
