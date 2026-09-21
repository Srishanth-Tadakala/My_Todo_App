"""
Hackathons Tests
"""

import pytest


@pytest.mark.asyncio
async def test_hackathon_crud(client, auth_headers):
    payload = {
        "name": "Global Hackfest 2026",
        "organizer": "Tech University",
        "submission_deadline": "2026-11-20T18:00:00Z",
        "website_url": "https://hackfest2026.com",
        "team_name": "Antigravity Devs",
        "status": "REGISTERED",
    }
    res = await client.post("/api/v1/hackathons", json=payload, headers=auth_headers)
    assert res.status_code == 201
    hack = res.json()
    assert hack["name"] == "Global Hackfest 2026"
    assert hack["status"] == "REGISTERED"
    hack_id = hack["id"]

    # Update status
    up_res = await client.put(
        f"/api/v1/hackathons/{hack_id}",
        json={"status": "SUBMITTED"},
        headers=auth_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "SUBMITTED"

    # Delete
    del_res = await client.delete(f"/api/v1/hackathons/{hack_id}", headers=auth_headers)
    assert del_res.status_code == 200
