import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.database import Base, get_db

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

    # Prevent lifespan from connecting to the production database
    with patch.object(Base.metadata, "create_all"):
        with patch("app.api.runs.run_pipeline", new_callable=AsyncMock):
            with TestClient(app) as c:
                yield c

    app.dependency_overrides.clear()
