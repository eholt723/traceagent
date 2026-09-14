import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.rate_limit import _hits as _rate_limit_hits

_TEST_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def engine():
    _engine = create_engine(
        _TEST_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=_engine)
    yield _engine
    _engine.dispose()


@pytest.fixture(scope="function")
def db(engine):
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSession()
    yield session
    session.close()


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    # Rate limiting and the origin guard are disabled by default in tests;
    # individual tests opt in via monkeypatch to exercise them.
    _rate_limit_hits.clear()
    original_limit = settings.run_rate_limit
    original_origin_check = settings.same_origin_check_enabled
    settings.run_rate_limit = 0
    settings.same_origin_check_enabled = False

    # Prevent lifespan from connecting to the production database
    with patch.object(Base.metadata, "create_all"):
        with patch("app.api.runs.run_pipeline", new_callable=AsyncMock):
            with TestClient(app) as c:
                yield c

    settings.run_rate_limit = original_limit
    settings.same_origin_check_enabled = original_origin_check
    _rate_limit_hits.clear()
    app.dependency_overrides.clear()
