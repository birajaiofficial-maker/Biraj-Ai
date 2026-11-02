import logging
import os
import threading
import time
from collections import OrderedDict

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.ai import router as ai_router
from app.database import SessionLocal, init_db
from app.models import TenantAPIKey, TenantUsageLog
from app.security import hash_api_key
from app.tenants import router as tenant_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="BIRAJ AI",
    description="API-first AI Customer Support & Business Automation platform",
    version="0.5.0",
)

redis_client = None
# Bounded process-local fallback prevents a Redis outage from denying every
# authenticated request. It is intentionally an emergency, per-process limit;
# Redis remains the authoritative shared limiter when healthy.
_local_rate_limits = OrderedDict()
_local_rate_limit_lock = threading.Lock()
_LOCAL_RATE_LIMIT_MAX_TENANTS = 10000

RATE_LIMIT_SCRIPT = """
local count = redis.call('INCR', KEYS[1])
if count == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
local ttl = redis.call('TTL', KEYS[1])
return {count, ttl}
"""


def get_redis_client():
    global redis_client
    redis_url = os.getenv("REDIS_URL")
    if not redis_url:
        return None
    if redis_client is None:
        from redis.asyncio import Redis

        redis_client = Redis.from_url(redis_url, decode_responses=True)
    return redis_client


def _consume_local_rate_limit(tenant_id: str, limit: int, window: int):
    """Return (allowed, remaining, retry_after) for emergency local throttling."""
    now = time.monotonic()
    with _local_rate_limit_lock:
        # Remove expired entries first to keep the fallback store bounded.
        expired = [
            key for key, (_, reset_at) in _local_rate_limits.items()
            if reset_at <= now
        ]
        for key in expired:
            _local_rate_limits.pop(key, None)

        entry = _local_rate_limits.get(tenant_id)
        if entry is None or entry[1] <= now:
            count = 1
            reset_at = now + window
        else:
            count, reset_at = entry
            count += 1

        _local_rate_limits[tenant_id] = (count, reset_at)
        _local_rate_limits.move_to_end(tenant_id)

        while len(_local_rate_limits) > _LOCAL_RATE_LIMIT_MAX_TENANTS:
            _local_rate_limits.popitem(last=False)

        remaining = max(0, limit - count)
        retry_after = max(1, int(reset_at - now))
        return count <= limit, remaining, retry_after


# Local-development origins only. Configure production origins before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Admin-Key"],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Mode",
        "Retry-After",
    ],
)

app.include_router(tenant_router)
app.include_router(ai_router)


@app.middleware("http")
async def record_tenant_usage(request: Request, call_next):
    started = time.perf_counter()
    raw_key = request.headers.get("X-API-Key")
    tenant_id = None

    # Resolve the tenant once, then apply shared Redis or emergency local limits.
    if raw_key and os.getenv("REDIS_URL"):
        db = SessionLocal()
        try:
            key_record = db.query(TenantAPIKey).filter(
                TenantAPIKey.key_hash == hash_api_key(raw_key),
                TenantAPIKey.is_active.is_(True),
            ).first()
            if key_record is not None and key_record.tenant.is_active:
                tenant_id = key_record.tenant_id
        finally:
            db.close()

        if tenant_id is not None:
            limit = max(1, int(os.getenv("RATE_LIMIT_REQUESTS", "60")))
            window = max(1, int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60")))
            try:
                client = get_redis_client()
                # Lua keeps INCR and first-request expiry atomic across app instances.
                count, ttl = await client.eval(
                    RATE_LIMIT_SCRIPT,
                    1,
                    f"biraj:rate-limit:{tenant_id}",
                    window,
                )
                if int(count) > limit:
                    response = JSONResponse(
                        status_code=429,
                        content={"detail": "Tenant rate limit exceeded. Retry after the current window."},
                        headers={
                            "Retry-After": str(max(1, int(ttl))),
                            "X-RateLimit-Limit": str(limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Mode": "redis",
                        },
                    )
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    _record_usage(tenant_id, request, response.status_code, elapsed_ms)
                    return response
                request.state.rate_limit_headers = {
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": str(max(0, limit - int(count))),
                    "X-RateLimit-Mode": "redis",
                }
            except Exception:
                logger.exception("Redis rate limiter unavailable; using local emergency limit")
                fallback_limit = max(
                    1, int(os.getenv("RATE_LIMIT_FALLBACK_REQUESTS", str(limit)))
                )
                allowed, remaining, retry_after = _consume_local_rate_limit(
                    tenant_id, fallback_limit, window
                )
                request.state.rate_limit_headers = {
                    "X-RateLimit-Limit": str(fallback_limit),
                    "X-RateLimit-Remaining": str(remaining),
                    "X-RateLimit-Mode": "local-fallback",
                }
                if not allowed:
                    response = JSONResponse(
                        status_code=429,
                        content={"detail": "Tenant emergency rate limit exceeded. Retry after the current window."},
                        headers={
                            "Retry-After": str(retry_after),
                            "X-RateLimit-Limit": str(fallback_limit),
                            "X-RateLimit-Remaining": "0",
                            "X-RateLimit-Mode": "local-fallback",
                        },
                    )
                    elapsed_ms = (time.perf_counter() - started) * 1000
                    _record_usage(tenant_id, request, response.status_code, elapsed_ms)
                    return response

    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000

    if tenant_id is None and raw_key:
        # Preserve usage tracking when rate limiting is disabled or key is invalid.
        db = SessionLocal()
        try:
            key_record = db.query(TenantAPIKey).filter(
                TenantAPIKey.key_hash == hash_api_key(raw_key),
                TenantAPIKey.is_active.is_(True),
            ).first()
            if key_record is not None and key_record.tenant.is_active:
                tenant_id = key_record.tenant_id
        except Exception:
            db.rollback()
        finally:
            db.close()

    if tenant_id is not None:
        _record_usage(tenant_id, request, response.status_code, elapsed_ms)

    for header, value in getattr(request.state, "rate_limit_headers", {}).items():
        response.headers[header] = value
    return response


def _record_usage(tenant_id: str, request: Request, status_code: int, elapsed_ms: float):
    db = SessionLocal()
    try:
        db.add(TenantUsageLog(
            tenant_id=tenant_id,
            method=request.method,
            path=request.url.path[:255],
            status_code=status_code,
            latency_ms=round(elapsed_ms, 2),
        ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/", tags=["System"])
def home():
    return {
        "project": "BIRAJ AI",
        "message": "Welcome to BIRAJ AI API",
        "status": "running",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health():
    return {"status": "healthy", "service": "BIRAJ AI"}


@app.get("/api/v1/services", tags=["Services"])
def list_services():
    return {
        "version": "v1",
        "status": "foundation",
        "services": [
            {"id": "customer-support", "name": "AI Customer Support", "status": "planned"},
            {"id": "knowledge-base", "name": "AI Knowledge Base", "status": "planned"},
            {"id": "multilingual", "name": "AI Language Assistant", "status": "planned"},
        ],
    }
