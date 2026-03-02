import pytest
from fastapi.testclient import TestClient
from sqlalchemy import inspect

from app.main import app
from app.database import engine


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_tables_exist(client):
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "users" in tables
    assert "runs" in tables
    assert "steps" in tables
