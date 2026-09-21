"""
Certifications Tests
"""

import pytest


@pytest.mark.asyncio
async def test_certification_crud(client, auth_headers):
    payload = {
        "name": "AWS Certified Cloud Practitioner",
        "provider": "Amazon Web Services",
        "exam_date": "2026-11-25T14:00:00Z",
        "expiry_date": "2029-11-25T14:00:00Z",
        "status": "IN_PROGRESS",
    }
    res = await client.post("/api/v1/certifications", json=payload, headers=auth_headers)
    assert res.status_code == 201
    cert = res.json()
    assert cert["name"] == "AWS Certified Cloud Practitioner"
    cert_id = cert["id"]

    # Update status to EARNED
    up_res = await client.put(
        f"/api/v1/certifications/{cert_id}",
        json={"status": "EARNED", "credential_id": "AWS-CERT-998811"},
        headers=auth_headers,
    )
    assert up_res.status_code == 200
    assert up_res.json()["status"] == "EARNED"
    assert up_res.json()["credential_id"] == "AWS-CERT-998811"

    # Delete
    del_res = await client.delete(f"/api/v1/certifications/{cert_id}", headers=auth_headers)
    assert del_res.status_code == 200
