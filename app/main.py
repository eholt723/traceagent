import base64
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles

import app.models  # register all ORM models with Base before create_all
from app.database import engine, Base
from app.api.runs import router as runs_router
from app.api.users import router as users_router
from app.api.ws import router as ws_router


@asynccontextmanager
async def lifespan(application: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="TraceAgent",
    description="Observable Agentic Research Platform",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(runs_router)
app.include_router(users_router)
app.include_router(ws_router)


_FAVICON_B64 = (
    "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"
    "B3OXaaDOTwAAAABJRU5ErkJggg=="
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/favicon.png")
def favicon():
    return Response(content=base64.b64decode(_FAVICON_B64), media_type="image/png")


# Serve built React app in production (ui/dist must exist)
_dist = os.path.join(os.path.dirname(__file__), "..", "ui", "dist")
if os.path.isdir(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="static")
