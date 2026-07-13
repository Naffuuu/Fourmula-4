from datetime import date, timedelta

import pytest


@pytest.mark.anyio
async def test_syllabus_negotiation_offline_fallback(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Syllabus User",
            "email": "syllabus@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201080",
        },
    )
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    test_date = (date.today() + timedelta(days=6)).isoformat()
    resp = await client.post(
        "/api/v1/syllabus",
        json={
            "raw_text": (
                "Chapter 1 covers thermodynamics basics. "
                "Chapter 2 covers an optional field trip writeup that is never tested. "
                "Chapter 3 covers entropy and will be on the final exam."
            ),
            "test_date": test_date,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert len(body["summary_bullets"]) > 0
    assert len(body["study_plan"]) > 0
