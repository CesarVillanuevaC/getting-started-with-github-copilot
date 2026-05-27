import copy
from fastapi.testclient import TestClient
from src import app as app_module
from src.app import app


import pytest


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(app_module.activities)
    yield
    # restore original activities after each test
    app_module.activities.clear()
    app_module.activities.update(original)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success():
    client = TestClient(app)
    email = "tester@example.com"
    activity = "Chess Club"
    # ensure not already signed up
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 200
    assert email in app_module.activities[activity]["participants"]
    assert resp.json()["message"] == f"Signed up {email} for {activity}"


def test_signup_duplicate():
    client = TestClient(app)
    email = "duplicate@example.com"
    activity = "Chess Club"
    # add the email first
    if email not in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].append(email)

    resp = client.post(f"/activities/{activity}/signup", params={"email": email})
    assert resp.status_code == 400


def test_unregister_success():
    client = TestClient(app)
    email = "to_remove@example.com"
    activity = "Chess Club"
    # ensure email is present
    if email not in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].append(email)

    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 200
    assert email not in app_module.activities[activity]["participants"]
    assert resp.json()["message"] == f"Unregistered {email} from {activity}"


def test_unregister_not_registered():
    client = TestClient(app)
    email = "not_registered@example.com"
    activity = "Chess Club"
    if email in app_module.activities[activity]["participants"]:
        app_module.activities[activity]["participants"].remove(email)

    resp = client.post(f"/activities/{activity}/unregister", params={"email": email})
    assert resp.status_code == 400
