"""
Internships Tests
"""

import pytest


@pytest.mark.asyncio
async def test_internship_stages(client, auth_headers):
    payload = {
        "company": "Google",
        "role": "Software Engineering Intern",
        "application_deadline": "2026-10-30T23:59:59Z",
        "application_url": "https://careers.google.com/jobs/123",
        "status": "APPLIED",
    }
    res = await client.post("/api/v1/internships", json=payload, headers=auth_headers)
    assert res.status_code == 201
    intern = res.json()
    assert intern["company"] == "Google"
    assert intern["status"] == "APPLIED"
    intern_id = intern["id"]

    # Transition to INTERVIEW
    up_res = await client.put(
        f"/api/v1/internships/{intern_id}",
        json={"status": "INTERVIEW", "interview_at": "2026-11-05T15:00:00Z"},
        headers=auth_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "INTERVIEW"

    # Transition to OFFER
    offer_res = await client.put(
        f"/api/v1/internships/{intern_id}",
        json={"status": "OFFER"},
        headers=auth_headers,
    )
    assert offer_res.status_code == 200
    assert offer_res.json()["status"] == "OFFER"

    # Delete
    del_res = await client.delete(f"/api/v1/internships/{intern_id}", headers=auth_headers)
    assert del_res.status_code == 200
