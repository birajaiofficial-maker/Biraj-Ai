# BIRAJ AI

BIRAJ AI is an API-first, multi-tenant AI customer support and business automation platform.

## Current foundation

- FastAPI application, health endpoint, and interactive API docs
- Tenant and tenant API-key database models
- Admin-protected tenant provisioning and tenant activation/deactivation
- Hashed tenant API-key storage
- Tenant API-key listing, additive key creation, and revocation
- Tenant-scoped request usage summaries
- Middleware that records requests authenticated with an active tenant API key

AI model integration, knowledge retrieval, booking/order workflows, Redis rate limiting, and production deployment are not implemented yet.

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

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | API information |
| GET | `/health` | Health check |
| GET | `/api/v1/services` | Service catalogue |
| POST | `/api/v1/admin/tenants` | Create tenant; requires `X-Admin-Key` |
| PATCH | `/api/v1/admin/tenants/{tenant_id}/status` | Activate/deactivate tenant; requires `X-Admin-Key` |
| GET | `/api/v1/tenant/me` | Current tenant profile; requires `X-API-Key` |
| GET | `/api/v1/tenant/api-keys` | List current tenant's keys |
| POST | `/api/v1/tenant/api-keys` | Create an additional API key |
| DELETE | `/api/v1/tenant/api-keys/{key_id}` | Revoke one of the current tenant's keys |
| GET | `/api/v1/tenant/usage?days=30` | Usage summary for the last 1–90 days |

Tenant creation and API-key creation return a raw API key only once. Store it securely; only its SHA-256 hash is saved in the database.

**Key rotation behavior:** creating a new key does not automatically disable old keys. Create the replacement key, update the integrating application, verify it works, and then revoke the old key.

Usage middleware records requests only when the supplied `X-API-Key` resolves to an active key belonging to an active tenant. It is not a complete audit log.

## Important security and development status

This is an early development foundation, not production-ready. Automated tests and live runtime verification have not yet been completed. Redis rate limiting, database migrations, full audit logging, HTTPS, secure production secret management, tenant-isolation tests, and operational monitoring are still required.

The built-in `create_all` database initialization is for development; it does not modify existing tables when model columns change. Use Alembic migrations before evolving a persistent production database.

Never commit real API keys, passwords, or production secrets.
