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
    testing_session = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = testing_session()
        try:
            yield db
        finally:
            db.close()

    monkeypatch.setenv("BIRAJ_ADMIN_KEY", "test-admin-secret")
    monkeypatch.setattr(main, "SessionLocal", testing_session)
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


def test_cannot_revoke_another_tenants_api_key(client):
    tenant_a = create_tenant(client, "Isolation A")
    tenant_b = create_tenant(client, "Isolation B")

    tenant_b_keys = client.get(
        "/api/v1/tenant/api-keys",
        headers={"X-API-Key": tenant_b["api_key"]},
    )
    assert tenant_b_keys.status_code == 200
    foreign_key_id = tenant_b_keys.json()["api_keys"][0]["id"]

    response = client.delete(
        f"/api/v1/tenant/api-keys/{foreign_key_id}",
        headers={"X-API-Key": tenant_a["api_key"]},
    )
    assert response.status_code == 404

    still_active = client.get(
        "/api/v1/tenant/me",
        headers={"X-API-Key": tenant_b["api_key"]},
    )
    assert still_active.status_code == 200
    assert still_active.json()["tenant_id"] == tenant_b["tenant_id"]
