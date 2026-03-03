"""CloudWatch custom metrics. No-op when AWS credentials are absent."""
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_NAMESPACE = "TraceAgent"
_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    from app.config import settings
    if not settings.aws_access_key_id:
        return None
    try:
        import boto3
        _client = boto3.client(
            "cloudwatch",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
        return _client
    except Exception as exc:
        logger.warning("CloudWatch metrics client init failed: %s", exc)
        return None


def _put(metric_data: list[dict]) -> None:
    client = _get_client()
    if client is None:
        return
    ts = datetime.now(timezone.utc)
    for m in metric_data:
        m.setdefault("Timestamp", ts)
    try:
        client.put_metric_data(Namespace=_NAMESPACE, MetricData=metric_data)
    except Exception as exc:
        logger.warning("CloudWatch put_metric_data failed: %s", exc)


def emit_run_complete(duration_ms: int, loop_count: int) -> None:
    _put([
        {"MetricName": "RunsCompleted", "Value": 1, "Unit": "Count"},
        {"MetricName": "RunsFailed", "Value": 0, "Unit": "Count"},
        {"MetricName": "PipelineDurationMs", "Value": duration_ms, "Unit": "Milliseconds"},
        {"MetricName": "ReflectionLoops", "Value": loop_count, "Unit": "Count"},
        {"MetricName": "SearchLoopTriggered", "Value": 1 if loop_count > 0 else 0, "Unit": "Count"},
    ])


def emit_run_failed(rate_limit: bool = False) -> None:
    _put([
        {"MetricName": "RunsCompleted", "Value": 0, "Unit": "Count"},
        {"MetricName": "RunsFailed", "Value": 1, "Unit": "Count"},
        {"MetricName": "RateLimitErrors", "Value": 1 if rate_limit else 0, "Unit": "Count"},
    ])
