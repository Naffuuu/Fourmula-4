import pytest


@pytest.mark.anyio
async def test_sos_alert_creation_and_listing(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Sos User",
            "email": "sos@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201070",
        },
    )
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create = await client.post("/api/v1/sos", json={"location": "Library, 2nd floor"}, headers=headers)
    assert create.status_code == 201
    assert create.json()["status"] == "active"

    listing = await client.get("/api/v1/sos", headers=headers)
    assert any(a["location"] == "Library, 2nd floor" for a in listing.json())
