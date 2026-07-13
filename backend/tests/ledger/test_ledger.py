import pytest


@pytest.mark.anyio
async def test_ledger_entry_round_trip(client):
    signup = await client.post(
        "/api/v1/auth/signup",
        json={
            "name": "Ledger User",
            "email": "ledger@example.com",
            "password": "correcthorse123",
            "role": "student",
            "roll_number": "2201060",
        },
    )
    token = signup.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/ledger", json={"type": "cash", "amount": 40.0, "item_description": "Forced fund"}, headers=headers
    )
    await client.post(
        "/api/v1/ledger",
        json={"type": "food", "amount": 1.0, "item_description": "Confiscated paratha"},
        headers=headers,
    )
    await client.post(
        "/api/v1/ledger",
        json={"type": "food", "amount": 2.0, "item_description": "Confiscated snacks"},
        headers=headers,
    )

    summary = (await client.get("/api/v1/ledger", headers=headers)).json()
    assert summary["total_cash"] == 40.0
    assert summary["total_food_items"] == 3
    assert summary["caloric_intake_estimate_kcal"] == 3 * 250.0
    assert len(summary["entries"]) == 4
