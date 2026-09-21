"""
Search, Analytics, Devices, and Attachments Tests
"""

import pytest


@pytest.mark.asyncio
async def test_search_across_entities(client, auth_headers):
    # 1. Create a Todo with keyword DBMS
    await client.post(
        "/api/v1/todos",
        json={"title": "DBMS Indexing Study"},
        headers=auth_headers,
    )

    # 2. Create a Subject with DBMS
    await client.post(
        "/api/v1/subjects",
        json={"name": "Database Management Systems", "code": "DBMS-CS301"},
        headers=auth_headers,
    )

    # 3. Perform search
    res = await client.get("/api/v1/search?q=DBMS", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total_results"] >= 2
    types = [item["type"] for item in data["results"]]
    assert "TODO" in types
    assert "SUBJECT" in types


@pytest.mark.asyncio
async def test_analytics_summary(client, auth_headers):
    # Create and complete a task
    todo_res = await client.post(
        "/api/v1/todos",
        json={"title": "Analytics Task 1"},
        headers=auth_headers,
    )
    todo_id = todo_res.json()["id"]
    await client.post(f"/api/v1/todos/{todo_id}/complete", headers=auth_headers)

    # Fetch summary for today
    res = await client.get("/api/v1/analytics/summary?period=today", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["period"] == "today"
    assert data["tasks_completed"] >= 1
    assert data["completion_rate"] > 0


@pytest.mark.asyncio
async def test_expo_device_lifecycle_and_push(client, auth_headers):
    # Register device
    dev_res = await client.post(
        "/api/v1/notifications/devices",
        json={
            "expo_push_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]",
            "platform": "android",
            "device_name": "Pixel 8 Pro",
        },
        headers=auth_headers,
    )
    assert dev_res.status_code == 201
    dev = dev_res.json()
    assert dev["platform"] == "android"
    assert dev["is_active"] is True
    dev_id = dev["id"]

    # List devices
    list_devs = await client.get("/api/v1/notifications/devices", headers=auth_headers)
    assert list_devs.status_code == 200
    assert len(list_devs.json()) >= 1

    # Send test push notification
    push_res = await client.post(
        "/api/v1/notifications/test?title=Hello&body=World",
        headers=auth_headers,
    )
    assert push_res.status_code == 200
    assert push_res.json()["data"]["dispatched"] is True

    # Delete device
    del_res = await client.delete(f"/api/v1/notifications/devices/{dev_id}", headers=auth_headers)
    assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_attachments_flow(client, auth_headers):
    # 1. Get Presigned Upload URL
    up_res = await client.post(
        "/api/v1/attachments/upload-url?entity_type=TODO&file_name=syllabus.pdf",
        headers=auth_headers,
    )
    assert up_res.status_code == 200
    up_data = up_res.json()
    assert "upload_url" in up_data
    storage_path = up_data["storage_path"]

    # 2. Record attachment metadata
    rec_res = await client.post(
        "/api/v1/attachments/record",
        json={
            "entity_type": "TODO",
            "entity_id": "00000000-0000-0000-0000-000000000030",
            "file_name": "syllabus.pdf",
            "storage_path": storage_path,
            "mime_type": "application/pdf",
            "file_size": 204800,
        },
        headers=auth_headers,
    )
    assert rec_res.status_code == 201
    att_id = rec_res.json()["id"]

    # 3. List attachments for entity
    list_att = await client.get(
        "/api/v1/attachments/TODO/00000000-0000-0000-0000-000000000030",
        headers=auth_headers,
    )
    assert list_att.status_code == 200
    assert len(list_att.json()) == 1

    # 4. Delete attachment
    del_att = await client.delete(f"/api/v1/attachments/{att_id}", headers=auth_headers)
    assert del_att.status_code == 200
