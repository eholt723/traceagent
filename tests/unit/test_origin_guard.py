from app.config import settings


def test_blocks_request_with_no_origin_or_referer(client, monkeypatch):
    monkeypatch.setattr(settings, "same_origin_check_enabled", True)

    response = client.post("/runs", json={"query": "q", "is_public": True})

    assert response.status_code == 403


def test_blocks_request_with_mismatched_origin(client, monkeypatch):
    monkeypatch.setattr(settings, "same_origin_check_enabled", True)

    response = client.post(
        "/runs",
        json={"query": "q", "is_public": True},
        headers={"Origin": "https://evil-scraper.example"},
    )

    assert response.status_code == 403


def test_allows_request_with_matching_origin(client, monkeypatch):
    monkeypatch.setattr(settings, "same_origin_check_enabled", True)

    response = client.post(
        "/runs",
        json={"query": "q", "is_public": True},
        headers={"Origin": "https://eholt723-traceagent.hf.space"},
    )

    assert response.status_code == 201


def test_allows_request_with_matching_referer_when_origin_absent(client, monkeypatch):
    monkeypatch.setattr(settings, "same_origin_check_enabled", True)

    response = client.post(
        "/runs",
        json={"query": "q", "is_public": True},
        headers={"Referer": "https://eholt723-traceagent.hf.space/"},
    )

    assert response.status_code == 201


def test_allows_configured_extra_host(client, monkeypatch):
    monkeypatch.setattr(settings, "same_origin_check_enabled", True)
    monkeypatch.setattr(settings, "allowed_frontend_hosts", "eholt723-traceagent.hf.space,example.com")

    response = client.post(
        "/runs",
        json={"query": "q", "is_public": True},
        headers={"Origin": "https://example.com"},
    )

    assert response.status_code == 201


def test_disabled_by_default_allows_headerless_requests(client):
    response = client.post("/runs", json={"query": "q", "is_public": True})

    assert response.status_code == 201
