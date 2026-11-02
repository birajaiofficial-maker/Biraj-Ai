# BIRAJ AI — System Architecture

**Status:** Initial architecture baseline with a first Cloudflare Workers AI adapter implementation. Target design is proposed; implementation must be verified module by module.

## 1. Product boundary

BIRAJ AI is a standalone, API-first AI platform. Separate client apps own their UI and app-specific behavior and connect to BIRAJ AI through the BIRAJ AI API. The immediate objective is to complete and verify the reusable core platform before adding end-user services.

ChatGPT may be used as the external development assistant for planning, coding, review, debugging and GitHub work; it is not a BIRAJ AI runtime dependency.

## 2. Confirmed runtime policy

- Cloudflare Workers AI is the only approved runtime AI provider at this stage.
- OpenAI, Google Gemini, Groq and Ollama are not runtime providers.
- No automatic provider fallback is permitted.
- Inference is disabled by default until account configuration, model access, quota and billing safeguards are verified.
- No paid plan, paid usage or billing change may be enabled without explicit user approval.
- When inference is disabled, credentials are missing, or Cloudflare is unavailable or rejects a request, the API must stop safely and return a normalized error.

## 3. Logical layers

| Layer | Responsibility | Status |
|---|---|---|
| Client apps | User-facing interfaces and app-specific behavior | Separate apps; implementation planned |
| BIRAJ API boundary | Versioned request/response contract and authentication | Partially implemented |
| Backend / orchestration | Tenant validation, prompt assembly and request coordination | Initial implementation |
| Provider adapter | Provider-specific HTTP details and normalized errors | Initial Cloudflare adapter implemented |
| Runtime inference | Model execution hosted by Cloudflare Workers AI | External service; live account validation pending |
| Data layer | Persistent application data and migrations | Basic SQLAlchemy models exist; production DB and migrations pending |
| Memory / retrieval | Conversation state, memory and knowledge retrieval | Pending |
| Security | Identity, access policy, secrets, audit and rate controls | Partial foundation exists; hardening pending |
| Observability | Logs, metrics, traces and alerts | Planned |
| Deployment | Reproducible environments and release process | Pending |

## 4. Current request flow

1. A client app sends a request to the BIRAJ AI API with its tenant API key.
2. BIRAJ validates the tenant and request.
3. The AI route checks the inference-enabled configuration.
4. The Cloudflare adapter validates its account ID, token and @cf/ model identifier.
5. The adapter calls the account-scoped Workers AI REST endpoint.
6. The adapter validates the upstream response and returns normalized output.
7. BIRAJ returns the response to the client app.

The current chat route is a minimal first integration, not the final orchestration, context, memory or streaming architecture.

## 5. Verified repository baseline

The inspected repository contains:
- tenant and tenant API-key data models;
- admin-protected tenant provisioning and activation/deactivation;
- hashed tenant API-key storage, key listing, creation and revocation;
- tenant-scoped usage summaries and request-recording middleware;
- optional Redis-backed per-tenant fixed-window rate limiting;
- app/ai.py with authenticated AI status and chat routes;
- app/providers/cloudflare_workers_ai.py with an HTTPX-based Cloudflare Workers AI adapter;
- adapter and API test files;
- a GitHub Actions test workflow.

These are existing foundations, not proof of production readiness. The live Cloudflare account, token permissions, quota and billing behavior have not been verified by these code inspections.

## 6. Technology inventory

| Area | Current repository evidence | Decision |
|---|---|---|
| Language | Python | Existing |
| API framework | FastAPI | Existing |
| ORM | SQLAlchemy 2 | Existing |
| Local database | SQLite default | Development default only |
| Production database | PostgreSQL is configurable per README | Pending production decision |
| Rate limiting | Optional Redis integration | Existing; resilience review pending |
| Runtime AI provider | Cloudflare Workers AI REST API | Confirmed |
| Initial chat model | @cf/zai-org/glm-4.7-flash | Configured default; live quota/access verification pending |
| Frontend | No frontend framework established | Separate client apps; pending |
| Deployment target | Not established | Pending |

## 7. Interfaces still to complete

- Provider contract: generation, streaming, model metadata, timeout policy and normalized errors.
- API contracts: versioning, authentication, validation, error envelope and request IDs.
- Persistence contracts: migrations, transaction boundaries and data ownership.
- Memory contracts: read/write scope, retention, deletion and tenant isolation.
- Operational contracts: quota accounting, usage limits, readiness, monitoring and incident behavior.

## 8. Remaining decisions and work

See Decision Log. Remaining work includes production database and migrations, memory design, API hardening, rate-limit resilience, observability, deployment, and verification of Cloudflare account-level quota and billing safeguards.
