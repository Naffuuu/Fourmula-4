import pytest


@pytest.mark.anyio
async def test_student_can_generate_seating_chart(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Seating Student",
            "email": "seating.student@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201091",
        },
    )
    token = signup.json()["access_token"]

    roster = [
        {"name": "A", "roll_number": "2201092", "height_cm": 150, "constraints": None},
        {"name": "B", "roll_number": "2201093", "height_cm": 160, "constraints": None},
        {"name": "C", "roll_number": "2201094", "height_cm": 155, "constraints": None},
    ]

    resp = await client.post(
        "/api/v1/seating/generate",
        json={
            "roster": roster,
            "rows": 2,
            "cols": 2,
            "podium_position": [0, 0],
            "kuddus_seat": [1, 1],
            "aisle_columns": [],
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["layout_id"]
    assert body["average_sightline_score"] >= 0
    assert len(body["grid"]) == 2
