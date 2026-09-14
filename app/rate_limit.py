"""Per-IP rate limiting for endpoints that trigger the agent pipeline.

In-memory sliding window — fine for a single-process deployment (one uvicorn
worker on Hugging Face Spaces / EC2). Exists to stop automated/bot traffic
from burning Groq + Tavily free-tier quota, not to police legitimate visitors.
"""
import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request

from app.config import settings

_lock = Lock()
_hits: dict[str, list[float]] = defaultdict(list)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_run_rate_limit(request: Request) -> None:
    if settings.run_rate_limit <= 0:
        return

    ip = _client_ip(request)
    now = time.monotonic()
    window_start = now - settings.run_rate_limit_window_seconds

    with _lock:
        hits = [t for t in _hits[ip] if t > window_start]
        if len(hits) >= settings.run_rate_limit:
            retry_after = int(hits[0] + settings.run_rate_limit_window_seconds - now) + 1
            _hits[ip] = hits
            raise HTTPException(
                status_code=429,
                detail="Too many runs from this IP. Please wait a few minutes before starting another.",
                headers={"Retry-After": str(retry_after)},
            )
        hits.append(now)
        _hits[ip] = hits
