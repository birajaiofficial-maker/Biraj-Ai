import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import main
from app.database import Base, get_db


@pytest.fixture
def client(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setenv("BIRAJ_ADMIN_KEY", "test-admin-secret")
    monkeypatch.setattr(main, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(main, "init_db", lambda: None)
    main.app.dependency_overrides[get_db] = override_get_db

    with TestClient(main.app) as test_client:
        yield test_client

    main.app.dependency_overrides.clear()
    engine.dispose()


def create_tenant(client, name):
    response = client.post(
        "/api/v1/admin/tenants",
        headers={"X-Admin-Key": "test-admin-secret"},
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


def test_health_and_service_catalogue(client):
    assert client.get("/health").json()["status"] == "healthy"
    services = client.get("/api/v1/services")
    assert services.status_code == 200
    assert services.json()["services"]


def test_tenant_keys_usage_and_isolation(client):
    tenant_a = create_tenant(client, "Company A")
    tenant_b = create_tenant(client, "Company B")
    key_a = tenant_a["api_key"]
    key_b = tenant_b["api_key"]
    headers_a = {"X-API-Key": key_a}

    profile = client.get("/api/v1/tenant/me", headers=headers_a)
    assert profile.status_code == 200
    assert profile.json()["tenant_id"] == tenant_a["tenant_id"]

    listed = client.get("/api/v1/tenant/api-keys", headers=headers_a)
    assert listed.status_code == 200
    assert len(listed.json()["api_keys"]) == 1

    created = client.post("/api/v1/tenant/api-keys", headers=headers_a)
    assert created.status_code == 201
    new_key = created.json()["api_key"]

    # A tenant cannot revoke another tenant's key.
    foreign_revoke = client.delete(
        f"/api/v1/tenant/api-keys/{tenant_b['tenant_id']}",
        headers=headers_a,
    )
    assert foreign_revoke.status_code == 404

    new_key_id = created.json()["id"]
    revoked = client.delete(
        f"/api/v1/tenant/api-keys/{new_key_id}",
        headers=headers_a,
    )
    assert revoked.status_code == 200
    assert client.get(
        "/api/v1/tenant/me",
        headers={"X-API-Key": new_key},
    ).status_code == 401

    # The second tenant's key remains usable and isolated.
    other_profile = client.get(
        "/api/v1/tenant/me",
        headers={"X-API-Key": key_b},
    )
    assert other_profile.status_code == 200
    assert other_profile.json()["tenant_id"] == tenant_b["tenant_id"]

    usage = client.get("/api/v1/tenant/usage?days=30", headers=headers_a)
    assert usage.status_code == 200
    assert usage.json()["total_requests"] >= 2
    assert usage.json()["average_latency_ms"] >= 0


def test_admin_authentication_and_usage_validation(client):
    denied = client.post(
        "/api/v1/admin/tenants",
        json={"name": "No Admin"},
    )
    assert denied.status_code == 401

    tenant = create_tenant(client, "Company C")
    invalid_days = client.get(
        "/api/v1/tenant/usage?days=120",
        headers={"X-API-Key": tenant["api_key"]},
    )
    assert invalid_days.status_code == 422


def test_tenant_name_is_trimmed_before_length_validation(client):
    tenant = create_tenant(client, "  Example Tenant  ")
    assert tenant["tenant_name"] == "Example Tenant"

    whitespace_only = client.post(
        "/api/v1/admin/tenants",
        headers={"X-Admin-Key": "test-admin-secret"},
        json={"name": "   "},
    )
    assert whitespace_only.status_code == 422

    too_short_after_trimming = client.post(
        "/api/v1/admin/tenants",
        headers={"X-Admin-Key": "test-admin-secret"},
        json={"name": " A "},
    )
    assert too_short_after_trimming.status_code == 422


class FakeRedis:
    def __init__(self):
        self.counts = {}

    async def eval(self, script, number_of_keys, key, window):
        self.counts[key] = self.counts.get(key, 0) + 1
        return [self.counts[key], int(window)]


def test_redis_rate_limit_is_per_tenant_and_returns_retry_after(client, monkeypatch):
    fake_redis = FakeRedis()
    monkeypatch.setattr(main, "redis_client", fake_redis)
    monkeypatch.setenv("REDIS_URL", "redis://fake/0")
    monkeypatch.setenv("RATE_LIMIT_REQUESTS", "1")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")

    tenant_a = create_tenant(client, "Rate Limited A")
    tenant_b = create_tenant(client, "Rate Limited B")

    first_a = client.get(
        "/api/v1/tenant/me",
        headers={"X-API-Key": tenant_a["api_key"]},
    )
    assert first_a.status_code == 200
    assert first_a.headers["x-ratelimit-limit"] == "1"
    assert first_a.headers["x-ratelimit-remaining"] == "0"

    blocked_a = client.get(
        "/api/v1/tenant/me",
        headers={"X-API-Key": tenant_a["api_key"]},
    )
    assert blocked_a.status_code == 429
    assert blocked_a.headers["retry-after"] == "60"

    first_b = client.get(
        "/api/v1/tenant/me",
        headers={"X-API-Key": tenant_b["api_key"]},
    )
    assert first_b.status_code == 200
