# BIRAJ AI

BIRAJ AI is an API-first, multi-tenant AI customer support and business automation platform.

## Current foundation

- FastAPI application and interactive API docs
- Health and service catalogue endpoints
- Tenant and tenant API-key database models
- Hashed tenant API-key storage
- Admin-protected tenant provisioning
- Tenant-authenticated profile endpoint

AI model integration, knowledge retrieval, business workflows, rate limiting, audit logging, and production deployment are not implemented yet.

## Technology

- Python 3.11+
- FastAPI and Uvicorn
- SQLAlchemy 2
- SQLite for local development; PostgreSQL can be configured with a suitable driver

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set a long, random `BIRAJ_ADMIN_KEY` in `.env`, then start:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Main endpoints

- `GET /` — API information
- `GET /health` — health check
- `GET /api/v1/services` — service catalogue
- `POST /api/v1/admin/tenants` — create a tenant (requires `X-Admin-Key`)
- `GET /api/v1/tenant/me` — current tenant profile (requires `X-API-Key`)

Tenant creation returns the tenant API key once. Store it securely; only its SHA-256 hash is saved in the database.

## Important security status

This is an early development foundation, not production-ready. Before production, add database migrations, key rotation/revocation workflows, rate limiting, audit logs, HTTPS, secure secret management, tenant-scoped data access tests, and operational monitoring. The built-in `create_all` database initialization is for development; use Alembic migrations in production.

Never commit real API keys, passwords, or production secrets.
