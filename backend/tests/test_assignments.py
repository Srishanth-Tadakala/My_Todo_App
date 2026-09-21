"""
Assignments Tests
"""

import pytest


@pytest.mark.asyncio
async def test_assignment_crud(client, auth_headers):
    payload = {
        "title": "Computer Networks Lab 2",
        "description": "Packet sniffing using Wireshark",
        "due_at": "2026-10-20T23:59:59Z",
        "priority": "HIGH",
        "status": "NOT_STARTED",
        "submission_url": "https://classroom.google.com/c/123",
    }
    res = await client.post("/api/v1/assignments", json=payload, headers=auth_headers)
    assert res.status_code == 201
    assign = res.json()
    assert assign["title"] == "Computer Networks Lab 2"
    assign_id = assign["id"]

    # Update status to SUBMITTED
    up_res = await client.put(
        f"/api/v1/assignments/{assign_id}",
        json={"status": "SUBMITTED"},
        headers=auth_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "SUBMITTED"

    # List assignments
    list_res = await client.get("/api/v1/assignments", headers=auth_headers)
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # Delete
    del_res = await client.delete(f"/api/v1/assignments/{assign_id}", headers=auth_headers)
    assert del_res.status_code == 200
