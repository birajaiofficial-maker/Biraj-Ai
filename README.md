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
- Optional Redis-backed, shared per-tenant fixed-window rate limiting
- Initial self-hosted Ollama adapter for tenant-authenticated AI status and chat routes

## AI runtime (development)

The AI adapter talks only to a self-hosted Ollama server; it does not call OpenAI or Google Gemini.

Configuration:
- `OLLAMA_BASE_URL`: Ollama server URL (default `http://127.0.0.1:11434`)
- `BIRAJ_AI_MODEL`: model tag already installed in Ollama (default `qwen2.5:0.5b`)

Endpoints (both require a valid tenant `X-API-Key`):
- `GET /api/v1/ai/status`: reports the configured local provider and model; it does not test connectivity
- `POST /api/v1/ai/chat`: sends one non-streaming user message to Ollama

Example request body:
```json
{"message":"Namaste, BIRAJ AI"}
```

Start Ollama separately and pull the configured model before chat requests can succeed. If Ollama is unreachable, the API returns HTTP 503. The default model is a small development choice, not a claim that it is trained by BIRAJ AI. Model licensing and hardware requirements must be reviewed before deployment.

## Technology

- Python 3.11+
- FastAPI and Uvicorn
- SQLAlchemy 2
- Redis 5/6 for distributed rate limiting (optional in development)
- SQLite for local development; PostgreSQL can be configured with a suitable driver
- Ollama for the optional self-hosted open-weight model runtime

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
| GET | `/api/v1/ai/status` | Local AI runtime configuration; tenant key required |
| POST | `/api/v1/ai/chat` | Send a message to local Ollama; tenant key required |
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

### Tenant rate limiting

Set `REDIS_URL` to enable a Redis-backed fixed-window limit. Defaults are 60 requests per tenant per 60 seconds; override them with `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW_SECONDS`. Limits are shared across application instances because counters live in Redis. Successful responses include `X-RateLimit-Limit` and `X-RateLimit-Remaining`; exceeded requests return HTTP 429 with `Retry-After`. Admin and requests without a valid active tenant key are not counted by this limiter. If Redis is configured but unavailable, authenticated tenant requests fail closed with HTTP 503. If `REDIS_URL` is unset, rate limiting is disabled.

## Important security and development status

This is an early development foundation, not production-ready. Automated tests and live runtime verification have not yet been completed. The Ollama adapter is an initial integration only; the model server has not been provisioned or verified. Database migrations, full audit logging, HTTPS, secure production secret management, and operational monitoring are still required. Redis rate limiting is implemented but requires a managed Redis service and production configuration.

The built-in `create_all` database initialization is for development; it does not modify existing tables when model columns change. Use Alembic migrations before evolving a persistent production database.

Never commit real API keys, passwords, or production secrets.
