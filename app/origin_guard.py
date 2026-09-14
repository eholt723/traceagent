"""Reject run-creating requests that didn't come from the TraceAgent frontend.

The production UI is served same-origin, and browsers always send an Origin
header (and usually Referer) on POST fetch requests, even for same-origin
calls. Scripts that hit the API directly, without ever loading the page,
typically omit these headers or set them to something else. Filtering on
that is a cheap way to cut scripted abuse without a CAPTCHA or any change
to the no-login UX for real visitors.
"""
from urllib.parse import urlparse

from fastapi import HTTPException, Request

from app.config import settings

_ALWAYS_ALLOWED_HOSTS = {"localhost", "127.0.0.1"}


def _allowed_hosts() -> set[str]:
    configured = {h.strip() for h in settings.allowed_frontend_hosts.split(",") if h.strip()}
    return _ALWAYS_ALLOWED_HOSTS | configured


def enforce_same_origin(request: Request) -> None:
    if not settings.same_origin_check_enabled:
        return

    header_value = request.headers.get("origin") or request.headers.get("referer")
    host = urlparse(header_value).hostname if header_value else None

    if host is None or host not in _allowed_hosts():
        raise HTTPException(
            status_code=403,
            detail="Requests must originate from the TraceAgent app.",
        )
