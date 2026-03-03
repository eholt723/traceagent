"""
Quick diagnostic: tests boto3 credentials and writes a log event to CloudWatch.
Run with: .venv/bin/python scripts/test_cloudwatch.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings

if not settings.aws_access_key_id:
    print("ERROR: AWS_ACCESS_KEY_ID not set in .env")
    sys.exit(1)

import boto3
import time

print(f"Region:    {settings.aws_region}")
print(f"Log group: {settings.cloudwatch_log_group}")
print(f"Key ID:    {settings.aws_access_key_id[:8]}...")

client = boto3.client(
    "logs",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)

log_group = settings.cloudwatch_log_group
log_stream = "test-direct"

# Create log group (ok if it already exists)
try:
    client.create_log_group(logGroupName=log_group)
    print(f"Created log group: {log_group}")
except client.exceptions.ResourceAlreadyExistsException:
    print(f"Log group already exists: {log_group}")

# Create log stream
try:
    client.create_log_stream(logGroupName=log_group, logStreamName=log_stream)
    print(f"Created log stream: {log_stream}")
except client.exceptions.ResourceAlreadyExistsException:
    print(f"Log stream already exists: {log_stream}")

# Write a log event
ts = int(time.time() * 1000)
client.put_log_events(
    logGroupName=log_group,
    logStreamName=log_stream,
    logEvents=[{"timestamp": ts, "message": "test_cloudwatch.py: direct boto3 write works"}],
)

print("SUCCESS: log event written. Check CloudWatch > Log groups > traceagent > test-direct")
