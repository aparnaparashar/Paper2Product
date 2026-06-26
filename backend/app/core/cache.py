"""
Upstash Redis cache — used to broadcast agent progress
so the SSE stream can read it without hitting the DB every 2s.
Falls back to no-op if Upstash is not configured.
"""
import json
from app.core.config import get_settings

settings = get_settings()
_client = None


def _get_client():
    global _client
    if _client is None and settings.upstash_redis_rest_url:
        try:
            from upstash_redis import Redis
            _client = Redis(
                url=settings.upstash_redis_rest_url,
                token=settings.upstash_redis_rest_token,
            )
        except Exception:
            _client = None
    return _client


def set_progress(project_id: str, data: dict, ttl: int = 3600):
    client = _get_client()
    if client:
        try:
            client.setex(f"progress:{project_id}", ttl, json.dumps(data))
        except Exception:
            pass


def get_progress(project_id: str) -> dict | None:
    client = _get_client()
    if client:
        try:
            raw = client.get(f"progress:{project_id}")
            return json.loads(raw) if raw else None
        except Exception:
            pass
    return None


def delete_progress(project_id: str):
    client = _get_client()
    if client:
        try:
            client.delete(f"progress:{project_id}")
        except Exception:
            pass
