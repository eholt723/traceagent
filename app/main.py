from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # register all ORM models with Base before create_all
from app.database import engine, Base


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TraceAgent",
    description="Observable Agentic Research Platform",
    lifespan=lifespan,
)


@app.get("/health")
def health():
    return {"status": "ok"}
