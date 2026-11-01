import hashlib
import secrets

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Tenant, TenantAPIKey


def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def generate_tenant_api_key() -> str:
    return "biraj_live_" + secrets.token_urlsafe(32)


def get_current_tenant(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    db: Session = Depends(get_db),
) -> Tenant:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-API-Key header",
        )

    key_record = (
        db.query(TenantAPIKey)
        .filter(
            TenantAPIKey.key_hash == hash_api_key(x_api_key),
            TenantAPIKey.is_active.is_(True),
        )
        .first()
    )

    if key_record is None or not key_record.tenant.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    return key_record.tenant
