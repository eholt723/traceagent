import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_upsert_user_create(client):
    user_uuid = str(uuid.uuid4())
    response = client.post("/users/upsert", json={"uuid": user_uuid, "name": "Test User"})
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == user_uuid
    assert data["name"] == "Test User"


def test_upsert_user_update_name(client):
    user_uuid = str(uuid.uuid4())
    client.post("/users/upsert", json={"uuid": user_uuid, "name": "Old Name"})
    response = client.post("/users/upsert", json={"uuid": user_uuid, "name": "New Name"})
    assert response.status_code == 200
    assert response.json()["name"] == "New Name"


def test_create_run(client):
    response = client.post("/runs", json={"query": "test research topic", "is_public": True})
    assert response.status_code == 201
    data = response.json()
    assert data["query"] == "test research topic"
    assert data["status"] == "pending"
    assert data["step_count"] == 0


def test_list_runs(client):
    response = client.get("/runs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_run_with_steps(client):
    create_resp = client.post("/runs", json={"query": "run detail test", "is_public": True})
    run_id = create_resp.json()["id"]
    response = client.get(f"/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run_id
    assert data["status"] == "complete"
    assert len(data["steps"]) > 0
    step_types = [s["step_type"] for s in data["steps"]]
    assert "planner" in step_types
    assert "synthesis" in step_types


def test_get_run_not_found(client):
    response = client.get("/runs/999999")
    assert response.status_code == 404


def test_fork_run(client):
    original = client.post("/runs", json={"query": "original query", "is_public": True})
    run_id = original.json()["id"]
    response = client.post(f"/runs/{run_id}/fork", json={"query": "forked query", "is_public": True})
    assert response.status_code == 201
    data = response.json()
    assert data["query"] == "forked query"
    assert data["forked_from_id"] == run_id


def test_fork_run_not_found(client):
    response = client.post("/runs/999999/fork", json={"query": "forked query", "is_public": True})
    assert response.status_code == 404
