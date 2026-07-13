import pytest

from app.models.misc import RulebookEntry


@pytest.mark.anyio
async def test_factcheck_without_seeded_rulebook_returns_503(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Fact User",
            "email": "fact@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201090",
        },
    )
    token = signup.json()["access_token"]
    resp = await client.post(
        "/api/v1/factcheck", json={"claim": "Can they charge for seats?"}, headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 503


@pytest.mark.anyio
async def test_factcheck_matches_seeded_rule(client, db_session):
    db_session.add(
        RulebookEntry(
            rule_text="Students may not be charged any fee for seating assignments.",
            source_section="4.2",
        )
    )
    await db_session.commit()

    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Fact User 2",
            "email": "fact2@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201091",
        },
    )
    token = signup.json()["access_token"]
    resp = await client.post(
        "/api/v1/factcheck",
        json={"claim": "Is it true I have to pay for my seat assignment?"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["source_section"] == "4.2"
