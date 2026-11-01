import hmac
import os

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant, TenantAPIKey
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
