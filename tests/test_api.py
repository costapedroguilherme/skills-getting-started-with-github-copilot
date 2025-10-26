from fastapi.testclient import TestClient
import pytest

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    # Create a shallow copy of original participants to restore after each test
    original = {k: v["participants"][:] for k, v in activities.items()}
    yield
    for k, v in original.items():
        activities[k]["participants"] = v[:]


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_prevent_duplicate():
    client = TestClient(app)
    activity = "Chess Club"
    email = "test_student@example.com"

    # Ensure not present
    assert email not in activities[activity]["participants"]

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Duplicate signup should return 400
    resp2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 400


def test_unregister():
    client = TestClient(app)
    activity = "Chess Club"
    email = "temp_remove@example.com"

    # Sign up first
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert email in activities[activity]["participants"]

    # Now unregister
    resp2 = client.delete(f"/activities/{activity}/signup?email={email}")
    assert resp2.status_code == 200
    assert email not in activities[activity]["participants"]
