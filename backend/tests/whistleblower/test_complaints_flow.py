import pytest


async def _signup(client, email, role, roll_number=None):
    resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": f"{role.title()} User",
            "email": email,
            "password": "correcthorse123",
            "role": role,
            "roll_number": roll_number,
        },
    )
    return resp.json()["access_token"]


@pytest.mark.anyio
async def test_complaint_submission_never_exposes_submitter(client):
    student_token = await _signup(client, "whistle@example.com", "student", "2201010")
    captain_token = await _signup(client, "captain2@example.com", "second_captain")

    submit = await client.post(
        "/api/v1/complaints",
        json={"category": "tiffin_theft", "description": "My tiffin was taken without any reason given at all."},
        headers={"Authorization": f"Bearer {student_token}"},
    )
    assert submit.status_code == 201
    complaint = submit.json()
    assert "user_id" not in complaint
    assert "submitter" not in complaint

    listing = await client.get("/api/v1/complaints", headers={"Authorization": f"Bearer {captain_token}"})
    assert listing.status_code == 200
    assert any(c["id"] == complaint["id"] for c in listing.json())


@pytest.mark.anyio
async def test_strike_escalation_caps_at_three(client):
    await _signup(client, "whistle2@example.com", "student", "2201011")
    captain_token = await _signup(client, "captain3@example.com", "third_captain")

    complaint_ids = []
    for i in range(4):
        student_token = await _signup(client, f"whistle_multi_{i}@example.com", "student", f"22011{i}")
        submit = await client.post(
            "/api/v1/complaints",
            json={"category": "bribes", "description": f"Bribe complaint number {i} with enough detail to pass."},
            headers={"Authorization": f"Bearer {student_token}"},
        )
        complaint_ids.append(submit.json()["id"])

    levels = []
    for cid in complaint_ids:
        resp = await client.post(
            f"/api/v1/complaints/{cid}/strike",
            headers={"Authorization": f"Bearer {captain_token}"},
        )
        levels.append(resp.json()["warning_level"])

    assert levels == [1, 2, 3, 3]
