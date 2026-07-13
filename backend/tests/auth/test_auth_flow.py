import pytest


@pytest.mark.anyio
async def test_signup_creates_account_and_logs_in(client):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Test Student",
            "email": "test.student@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201099",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["user"]["email"] == "test.student@example.com"
    assert "access_token" in body
    assert "akp_refresh_token" in resp.cookies


@pytest.mark.anyio
async def test_signup_duplicate_email_rejected(client):
    payload = {
        "name": "Dup User",
        "email": "dup@example.com",
        "password": "correcthorse123",
        "role": "student",
        "roll_number": "2201050",
    }
    first = await client.post("/api/v1/auth/signup", json=payload)
    assert first.status_code == 201

    second = await client.post("/api/v1/auth/signup", json=payload)
    assert second.status_code == 409


@pytest.mark.anyio
async def test_login_wrong_password_returns_401(client):
    await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Wrongpass User",
            "email": "wrongpass@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201077",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login", json={"email": "wrongpass@example.com", "password": "not-the-password"}
    )
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_me_requires_authentication(client):
    resp = await client.get("/api/v1/auth/me")
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_me_returns_current_user_with_valid_token(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Me Endpoint User",
            "email": "me.endpoint@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201033",
        },
    )
    token = signup.json()["access_token"]

    resp = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me.endpoint@example.com"


@pytest.mark.anyio
async def test_student_cannot_access_captain_only_route(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Regular Student",
            "email": "regular.student@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201044",
        },
    )
    token = signup.json()["access_token"]

    resp = await client.get("/api/v1/complaints", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403
