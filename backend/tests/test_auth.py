"""
Authentication and Profile Tests
"""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_check(client):
    res = await client.get("/health/ready")
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "ready"


@pytest.mark.asyncio
async def test_sign_up(client):
    payload = {
        "email": "student@example.com",
        "password": "Password123!",
        "full_name": "Test Student",
        "timezone": "Asia/Kolkata",
    }
    res = await client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "student@example.com"
    assert data["user"]["full_name"] == "Test Student"


@pytest.mark.asyncio
async def test_login(client):
    payload = {
        "email": "student@example.com",
        "password": "Password123!",
    }
    res = await client.post("/api/v1/auth/login", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_unauthorized_request(client):
    res = await client.get("/api/v1/auth/me")
    assert res.status_code == 401
    assert res.json()["success"] is False
    assert res.json()["error"]["code"] == "MISSING_AUTH_HEADER"


@pytest.mark.asyncio
async def test_invalid_token(client):
    res = await client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert res.status_code == 401
    assert res.json()["success"] is False


@pytest.mark.asyncio
async def test_authenticated_me(client, auth_headers):
    res = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == "00000000-0000-0000-0000-000000000001"
