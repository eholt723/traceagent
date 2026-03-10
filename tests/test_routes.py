import uuid
from unittest.mock import patch

from app import crud
from app.schemas.step import StepCreate, StepType


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
    client.post("/runs", json={"query": "list test query", "is_public": True})
    response = client.get("/runs")
    assert response.status_code == 200
    runs = response.json()
    assert isinstance(runs, list)
    assert len(runs) >= 1


def test_get_run_with_steps(client, db):
    create_resp = client.post("/runs", json={"query": "run detail test", "is_public": True})
    run_id = create_resp.json()["id"]

    # Pipeline is mocked — insert steps directly to verify GET /runs/{id} returns them
    for step_type, order in [
        (StepType.planner, 1),
        (StepType.search, 2),
        (StepType.reflection, 3),
        (StepType.synthesis, 4),
    ]:
        crud.create_step(db, StepCreate(
            run_id=run_id,
            step_type=step_type,
            step_order=order,
            input_data={"query": "run detail test"},
            output_data={"result": "mocked"},
        ))

    response = client.get(f"/runs/{run_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == run_id
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


def test_stats(client):
    with patch("app.api.stats.crud.get_stats", return_value={
        "total_runs": 5,
        "completed_runs": 4,
        "failed_runs": 1,
        "success_rate": 80,
        "avg_duration_ms": 12000,
        "avg_steps_per_run": 4.0,
        "reflection_loop_rate": 25,
        "runs_with_loops": 1,
    }):
        response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_runs"] == 5
    assert data["success_rate"] == 80
