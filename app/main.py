import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s: %(message)s")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import app.models  # register all ORM models with Base before create_all
from app.config import settings
from app.database import engine, Base
from app.api.runs import router as runs_router
from app.api.users import router as users_router
from app.api.ws import router as ws_router

# Add CloudWatch log handler when AWS credentials are present
if settings.aws_access_key_id:
    try:
        import boto3
        import watchtower
        _boto3_session = boto3.Session(
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        _cw_handler = watchtower.CloudWatchLogHandler(
            log_group=settings.cloudwatch_log_group,
            boto3_session=_boto3_session,
        )
        _cw_handler.setFormatter(logging.Formatter("%(levelname)s: %(name)s: %(message)s"))
        logging.getLogger().addHandler(_cw_handler)
        logging.getLogger(__name__).info(
            "CloudWatch logging enabled (group: %s, region: %s)",
            settings.cloudwatch_log_group, settings.aws_region
        )
    except Exception as _e:
        logging.getLogger(__name__).warning("CloudWatch setup failed, using console only: %s", _e)


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


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve built React app in production (ui/dist must exist)
_dist = os.path.join(os.path.dirname(__file__), "..", "ui", "dist")
if os.path.isdir(_dist):
    app.mount("/", StaticFiles(directory=_dist, html=True), name="static")
