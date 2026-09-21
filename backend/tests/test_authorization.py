"""
Multi-Tenant Authorization and User Isolation Tests
Ensures User A cannot access, modify, or delete User B's resources.
"""

import pytest


@pytest.mark.asyncio
async def test_cross_user_isolation(client, auth_headers, auth_headers_user2):
    # 1. User A creates a Todo
    todo_a_res = await client.post(
        "/api/v1/todos",
        json={"title": "Confidential Task User A"},
        headers=auth_headers,
    )
    assert todo_a_res.status_code == 201
    todo_a_id = todo_a_res.json()["id"]

    # 2. User B tries to view User A's Todo -> Must be 404 Not Found
    get_b = await client.get(f"/api/v1/todos/{todo_a_id}", headers=auth_headers_user2)
    assert get_b.status_code == 404

    # 3. User B tries to update User A's Todo -> Must be 404 Not Found
    put_b = await client.put(
        f"/api/v1/todos/{todo_a_id}",
        json={"title": "Hacked Title"},
        headers=auth_headers_user2,
    )
    assert put_b.status_code == 404

    # 4. User B tries to delete User A's Todo -> Must be 404 Not Found
    del_b = await client.delete(f"/api/v1/todos/{todo_a_id}", headers=auth_headers_user2)
    assert del_b.status_code == 404

    # 5. User B lists todos -> Must NOT contain User A's todo
    list_b = await client.get("/api/v1/todos", headers=auth_headers_user2)
    assert list_b.status_code == 200
    user_b_todo_ids = [t["id"] for t in list_b.json()["items"]]
    assert todo_a_id not in user_b_todo_ids

    # 6. User A can still retrieve own Todo
    get_a = await client.get(f"/api/v1/todos/{todo_a_id}", headers=auth_headers)
    assert get_a.status_code == 200
    assert get_a.json()["title"] == "Confidential Task User A"
