from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

engine = create_engine(settings.database_url) if settings.database_url else None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) if engine else None


class Base(DeclarativeBase):
    pass


def get_db():
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is not configured")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
