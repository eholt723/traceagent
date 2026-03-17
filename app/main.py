import logging
import os
from contextlib import asynccontextmanager

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(name)s: %(message)s")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

import app.models  # register all ORM models with Base before create_all
from app.config import settings
from app.database import engine, Base
from app.api.runs import router as runs_router
from app.api.stats import router as stats_router
from app.api.users import router as users_router
from app.api.ws import router as ws_router

# Add CloudWatch log handler when AWS credentials are present
if settings.aws_access_key_id:
    try:
        import boto3
        import watchtower
        _boto3_client = boto3.client(
            "logs",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        _cw_handler = watchtower.CloudWatchLogHandler(
            log_group_name=settings.cloudwatch_log_group,
            boto3_client=_boto3_client,
            send_interval=1,
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
    # create_all is kept for environments that haven't been migrated yet
    # (CI, local SQLite, fresh deployments before alembic upgrade head is run).
    # Once Alembic has been applied, the alembic_version table exists and
    # create_all becomes a no-op (SQLAlchemy skips tables that already exist).
    from sqlalchemy import inspect as sa_inspect
    if "alembic_version" not in sa_inspect(engine).get_table_names():
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
app.include_router(stats_router)
app.include_router(users_router)
app.include_router(ws_router)


@app.get("/health")
def health():
    return {"status": "ok"}


# Serve built React app in production (ui/dist must exist)
_dist = os.path.join(os.path.dirname(__file__), "..", "ui", "dist")
if os.path.isdir(_dist):
    _index = os.path.join(_dist, "index.html")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        # Serve actual files from dist; fall back to index.html for SPA routes
        candidate = os.path.join(_dist, full_path)
        if full_path and os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(
            _index,
            headers={"Cache-Control": "no-cache"},
        )

    app.mount("/assets", StaticFiles(directory=os.path.join(_dist, "assets")), name="assets")
