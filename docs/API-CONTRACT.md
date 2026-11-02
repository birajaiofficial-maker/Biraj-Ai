# BIRAJ AI — External API Contract (Current Baseline)

**Document status:** Describes the API currently implemented on `work/core-platform`; it is not a promise that every planned platform capability exists.  
**API prefix:** `/api/v1`  
**Authentication:** Tenant routes use `X-API-Key`. Admin provisioning/status routes use `X-Admin-Key`.

## 1. Contract principles

- Client applications call BIRAJ AI; they do not call the model provider directly.
- Tenant API keys are tenant-scoped. A tenant must not access another tenant's keys or usage.
- Send credentials only over HTTPS in deployed environments. Never place keys in URLs, browser-visible source, logs or public repositories.
- Provisioned tenant API keys are returned only at creation/rotation time. The server stores a SHA-256 hash, not the raw key.
- Cloudflare Workers AI is the only approved runtime provider. No provider fallback or automatic paid upgrade is allowed.
- Inference is disabled by default. The chat route returns a service-unavailable response while disabled or when provider configuration/upstream execution fails.

## 2. Request conventions

### Tenant authentication

Include this header on tenant endpoints:

```http
X-API-Key: biraj_live_<secret>
```

### Admin authentication

Include this header on admin endpoints:

```http
X-Admin-Key: <admin-secret>
```

### Content type

Send JSON request bodies with:

```http
Content-Type: application/json
```

### Current error shape

FastAPI currently returns errors using its standard `detail` field. The exact shape of validation errors may differ from application-raised HTTP errors. A single stable BIRAJ error envelope and request ID are not implemented yet.

## 3. Current endpoints

| Method | Path | Authentication | Purpose |
|---|---|---|---|
| GET | `/` | None | Basic service information |
| GET | `/health` | None | Basic process health response |
| GET | `/api/v1/services` | None | Current placeholder service catalogue |
| POST | `/api/v1/admin/tenants` | Admin | Provision a tenant and its first API key |
| PATCH | `/api/v1/admin/tenants/{tenant_id}/status` | Admin | Activate/deactivate a tenant |
| GET | `/api/v1/tenant/me` | Tenant | Read the authenticated tenant profile |
| GET | `/api/v1/tenant/api-keys` | Tenant | List key metadata (never raw secrets) |
| POST | `/api/v1/tenant/api-keys` | Tenant | Create an additional tenant API key |
| DELETE | `/api/v1/tenant/api-keys/{key_id}` | Tenant | Revoke one key owned by the tenant |
| GET | `/api/v1/tenant/usage?days=30` | Tenant | Read tenant usage summary |
| GET | `/api/v1/ai/status` | Tenant | Read provider/inference configuration status |
| POST | `/api/v1/ai/chat` | Tenant | Generate one response through Cloudflare Workers AI |

## 4. Endpoint request and response shapes

### POST /api/v1/admin/tenants

Request:

```json
{"name":"Example Company"}
```

- `name` is trimmed before validation.
- Length must be 2–160 characters after trimming.
- Requires configured `BIRAJ_ADMIN_KEY` and a matching `X-Admin-Key`.

Success (`201`):

```json
{
  "tenant_id": "<tenant-id>",
  "tenant_name": "Example Company",
  "api_key": "biraj_live_<secret>",
  "warning": "Save this API key securely. It cannot be retrieved later."
}
```

The raw API key is shown once. Store it securely.

### PATCH /api/v1/admin/tenants/{tenant_id}/status

Request:

```json
{"is_active":false}
```

Success (`200`):

```json
{"tenant_id":"<tenant-id>","is_active":false}
```

### GET /api/v1/tenant/me

Success (`200`):

```json
{
  "tenant_id":"<tenant-id>",
  "tenant_name":"Example Company",
  "status":"active",
  "created_at":"<timestamp>"
}
```

### GET /api/v1/tenant/api-keys

Success (`200`):

```json
{
  "api_keys":[
    {
      "id":"<key-id>",
      "prefix":"<non-secret-prefix>",
      "is_active":true,
      "created_at":"<timestamp>"
    }
  ]
}
```

### POST /api/v1/tenant/api-keys

No request body is required.

Success (`201`):

```json
{
  "id":"<key-id>",
  "api_key":"biraj_live_<secret>",
  "warning":"Save this key securely. Previous keys remain active until revoked."
}
```

Rotation currently creates an additional key; it does not automatically revoke previous keys.

### DELETE /api/v1/tenant/api-keys/{key_id}

Success (`200`):

```json
{"status":"revoked","key_id":"<key-id>"}
```

A key belonging to another tenant is not exposed; the route returns `404`.

### GET /api/v1/tenant/usage?days=30

- `days` is optional; default is 30.
- Allowed range is 1–90.

Success (`200`):

```json
{
  "period_days":30,
  "total_requests":0,
  "average_latency_ms":0.0,
  "requests_by_status":{"200":0}
}
```

The example values are illustrative only.

### GET /api/v1/ai/status

Requires a valid tenant API key. Success (`200`):

```json
{
  "service":"BIRAJ AI",
  "provider":"cloudflare_workers_ai",
  "enabled":false,
  "model":"<configured-model>",
  "tenant":"active"
}
```

This endpoint reports configuration; it does not prove live provider connectivity, available quota or billing status.

### POST /api/v1/ai/chat

Request:

```json
{"message":"Namaste"}
```

- `message` must contain 1–8,000 characters.
- Requires a valid tenant API key.
- Requires `BIRAJ_AI_ENABLED=true` and valid Cloudflare configuration.
- Current output-token setting is bounded to 1–2,048; default is 512.

Success (`200`):

```json
{
  "answer":"<model-response>",
  "provider":"cloudflare_workers_ai",
  "model":"<configured-model>"
}
```

If inference is disabled or Cloudflare configuration/upstream execution fails, the route currently returns `503`. No other provider is attempted.

## 5. Current authentication and status behavior

| Condition | Current behavior |
|---|---|
| Missing tenant API key | `401` |
| Invalid or revoked tenant API key | `401` |
| Inactive tenant | `401` |
| Missing/invalid admin key | `401` |
| Admin secret not configured | `503` |
| Tenant tries to revoke another tenant's key | `404` |
| Invalid request schema | FastAPI `422` |
| Inference disabled | `503` |
| Provider configuration or upstream failure | `503` |
| Tenant rate limit exceeded | `429` with `Retry-After` |

## 6. Explicit limitations and pending contract work

The current API is a foundation, not a finalized external integration contract. Before production clients depend on it, complete and test:

1. A stable versioned error envelope, machine-readable error codes and request/correlation IDs.
2. Explicit timeout, retry and idempotency policy. Do not retry non-idempotent operations automatically.
3. Streaming contract (not implemented).
4. Formal quota/usage semantics and response headers for all API routes.
5. Admin endpoint authorization model beyond a single shared admin secret.
6. API-key expiry, scoped permissions, audit events and safer rotation workflows.
7. Readiness/dependency health distinct from basic process liveness.
8. OpenAPI review and compatibility/versioning policy.
9. Pagination for key lists and usage details as data grows.
10. Tenant data retention, deletion and export semantics.

Do not implement these changes silently as part of documentation. Each needs an explicit design, tests and a recorded decision where it changes behavior.
