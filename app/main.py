from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # register all ORM models with Base before create_all
from app.database import engine, Base
from app.api.runs import router as runs_router
from app.api.users import router as users_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TraceAgent",
    description="Observable Agentic Research Platform",
    lifespan=lifespan,
)


app.include_router(runs_router)
app.include_router(users_router)


@app.get("/health")
def health():
    return {"status": "ok"}
