from app.config import settings
from app.rate_limit import _hits as _rate_limit_hits


def test_create_run_blocked_after_threshold(client, monkeypatch):
    monkeypatch.setattr(settings, "run_rate_limit", 2)
    monkeypatch.setattr(settings, "run_rate_limit_window_seconds", 600)

    r1 = client.post("/runs", json={"query": "q1", "is_public": True})
    r2 = client.post("/runs", json={"query": "q2", "is_public": True})
    r3 = client.post("/runs", json={"query": "q3", "is_public": True})

    assert r1.status_code == 201
    assert r2.status_code == 201
    assert r3.status_code == 429
    assert "Retry-After" in r3.headers


def test_fork_run_shares_rate_limit_budget_with_create_run(client, monkeypatch):
    monkeypatch.setattr(settings, "run_rate_limit", 2)
    monkeypatch.setattr(settings, "run_rate_limit_window_seconds", 600)

    original = client.post("/runs", json={"query": "original", "is_public": True})
    run_id = original.json()["id"]

    fork = client.post(f"/runs/{run_id}/fork", json={"query": "forked", "is_public": True})
    blocked = client.post(f"/runs/{run_id}/fork", json={"query": "forked again", "is_public": True})

    assert fork.status_code == 201
    assert blocked.status_code == 429


def test_different_ips_have_independent_budgets(client, monkeypatch):
    monkeypatch.setattr(settings, "run_rate_limit", 1)
    monkeypatch.setattr(settings, "run_rate_limit_window_seconds", 600)

    r1 = client.post("/runs", json={"query": "q1", "is_public": True},
                      headers={"X-Forwarded-For": "1.2.3.4"})
    r2 = client.post("/runs", json={"query": "q2", "is_public": True},
                      headers={"X-Forwarded-For": "5.6.7.8"})

    assert r1.status_code == 201
    assert r2.status_code == 201


def test_rate_limit_disabled_when_zero(client, monkeypatch):
    monkeypatch.setattr(settings, "run_rate_limit", 0)

    for _ in range(5):
        response = client.post("/runs", json={"query": "q", "is_public": True})
        assert response.status_code == 201

    assert _rate_limit_hits == {}
