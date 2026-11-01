import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.database import SessionLocal, init_db
from app.models import TenantAPIKey, TenantUsageLog
from app.security import hash_api_key
from app.tenants import router as tenant_router

app = FastAPI(
    title="BIRAJ AI",
    description="API-first AI Customer Support & Business Automation platform",
    version="0.3.0",
)

# Local-development origins only. Configure production origins before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key", "X-Admin-Key"],
)

app.include_router(tenant_router)


@app.middleware("http")
async def record_tenant_usage(request: Request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    elapsed_ms = (time.perf_counter() - started) * 1000
    raw_key = request.headers.get("X-API-Key")
    if raw_key:
        db = SessionLocal()
        try:
            key_record = db.query(TenantAPIKey).filter(
                TenantAPIKey.key_hash == hash_api_key(raw_key),
                TenantAPIKey.is_active.is_(True)
            ).first()
            if key_record is not None and key_record.tenant.is_active:
                db.add(TenantUsageLog(
                    tenant_id=key_record.tenant_id,
                    method=request.method,
                    path=request.url.path[:255],
                    status_code=response.status_code,
                    latency_ms=round(elapsed_ms, 2)
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
