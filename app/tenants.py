import hmac
import os
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant, TenantAPIKey, TenantUsageLog
from app.security import generate_tenant_api_key, get_current_tenant, hash_api_key

router = APIRouter(prefix="/api/v1", tags=["Tenants"])


class TenantCreate(BaseModel):
    name: str = Field(min_length=2, max_length=160)


@router.post("/admin/tenants", status_code=status.HTTP_201_CREATED)
def create_tenant(
    payload: TenantCreate,
    x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
    db: Session = Depends(get_db),
):
    configured_admin_key = os.getenv("BIRAJ_ADMIN_KEY", "")
    if not configured_admin_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Tenant provisioning is disabled: configure BIRAJ_ADMIN_KEY",
        )

    if not x_admin_key or not hmac.compare_digest(x_admin_key, configured_admin_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )

    tenant = Tenant(name=payload.name.strip())
    raw_api_key = generate_tenant_api_key()
    key_record = TenantAPIKey(
        tenant=tenant,
        key_hash=hash_api_key(raw_api_key),
        key_prefix=raw_api_key[:18],
    )

    db.add(tenant)
    db.add(key_record)
    db.commit()
    db.refresh(tenant)

    # The raw key is returned only once and is never stored in the database.
    return {
        "tenant_id": tenant.id,
        "tenant_name": tenant.name,
        "api_key": raw_api_key,
        "warning": "Save this API key securely. It cannot be retrieved later.",
    }


@router.get("/tenant/me")
def get_tenant_profile(tenant: Tenant = Depends(get_current_tenant)):
    return {
        "tenant_id": tenant.id,
        "tenant_name": tenant.name,
        "status": "active" if tenant.is_active else "inactive",
        "created_at": tenant.created_at,
    }


def require_admin_key(x_admin_key: str | None):
    configured = os.getenv("BIRAJ_ADMIN_KEY", "")
    if not configured:
        raise HTTPException(status_code=503, detail="Admin operations are disabled")
    if not x_admin_key or not hmac.compare_digest(x_admin_key, configured):
        raise HTTPException(status_code=401, detail="Invalid admin key")


@router.get("/tenant/api-keys")
def list_api_keys(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    keys = db.query(TenantAPIKey).filter(
        TenantAPIKey.tenant_id == tenant.id
    ).order_by(TenantAPIKey.created_at.desc()).all()
    return {"api_keys": [
        {"id": key.id, "prefix": key.key_prefix, "is_active": key.is_active,
         "created_at": key.created_at}
        for key in keys
    ]}


@router.post("/tenant/api-keys", status_code=status.HTTP_201_CREATED)
def rotate_api_key(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    raw_key = generate_tenant_api_key()
    record = TenantAPIKey(
        tenant_id=tenant.id,
        key_hash=hash_api_key(raw_key),
        key_prefix=raw_key[:18],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"id": record.id, "api_key": raw_key,
            "warning": "Save this key securely. Previous keys remain active until revoked."}


@router.delete("/tenant/api-keys/{key_id}")
def revoke_api_key(key_id: str, tenant: Tenant = Depends(get_current_tenant),
                   db: Session = Depends(get_db)):
    record = db.query(TenantAPIKey).filter(
        TenantAPIKey.id == key_id, TenantAPIKey.tenant_id == tenant.id
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail="API key not found")
    record.is_active = False
    db.commit()
    return {"status": "revoked", "key_id": record.id}


class TenantStatusUpdate(BaseModel):
    is_active: bool


@router.patch("/admin/tenants/{tenant_id}/status")
def update_tenant_status(tenant_id: str, payload: TenantStatusUpdate,
                         x_admin_key: str | None = Header(default=None, alias="X-Admin-Key"),
                         db: Session = Depends(get_db)):
    require_admin_key(x_admin_key)
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if tenant is None:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.is_active = payload.is_active
    db.commit()
    return {"tenant_id": tenant.id, "is_active": tenant.is_active}


@router.get("/tenant/usage")
def get_tenant_usage(days: int = 30, tenant: Tenant = Depends(get_current_tenant),
                     db: Session = Depends(get_db)):
    if days < 1 or days > 90:
        raise HTTPException(status_code=422, detail="days must be between 1 and 90")
    since = datetime.now(timezone.utc) - timedelta(days=days)
    summary = db.query(func.count(TenantUsageLog.id), func.avg(TenantUsageLog.latency_ms)).filter(
        TenantUsageLog.tenant_id == tenant.id,
        TenantUsageLog.created_at >= since
    ).one()
    statuses = db.query(TenantUsageLog.status_code, func.count(TenantUsageLog.id)).filter(
        TenantUsageLog.tenant_id == tenant.id,
        TenantUsageLog.created_at >= since
    ).group_by(TenantUsageLog.status_code).all()
    return {"period_days": days, "total_requests": summary[0] or 0,
            "average_latency_ms": round(float(summary[1] or 0), 2),
            "requests_by_status": {str(code): count for code, count in statuses}}
