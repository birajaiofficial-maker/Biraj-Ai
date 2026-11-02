# BIRAJ AI — System Architecture

**Status:** Initial architecture baseline. Target design is proposed; implementation must be verified module by module.

## 1. Product boundary

BIRAJ AI is being developed as a modular AI platform. The immediate objective is to complete and verify the reusable core platform before adding end-user services.

The runtime model must not depend on OpenAI or Google Gemini. ChatGPT may be used as the external development assistant for planning, coding, review, debugging, and GitHub work; that does not make it a BIRAJ AI runtime dependency.

## 2. Architectural principles

- Modular boundaries: each component has one clear responsibility and a documented interface.
- Replaceable model/runtime: avoid coupling application logic to one model vendor or inference engine.
- API-first backend with versioned interfaces.
- Secure-by-default authentication, authorization, secret handling, and tenant isolation where applicable.
- Observable and testable components, with health checks and structured operational signals.
- No duplicate implementations: one authoritative module and one authoritative document per concern.
- Prefer the simplest architecture that meets verified requirements; do not add infrastructure without a demonstrated need.

## 3. Logical layers

| Layer | Responsibility | Status |
|---|---|---|
| Client / UI | User-facing interface | Planned; framework pending |
| API boundary | Versioned request/response contract | Partially implemented; inspect and verify |
| Backend / orchestration | Authentication, validation, routing, coordination | Partially implemented |
| Model adapter | Provider/runtime-neutral model interface | Pending |
| Model runtime / inference engine | Loads and serves the selected open-weight model | Pending selection |
| Data layer | Persistent application data and migrations | Basic SQLAlchemy models exist; DB choice pending for production |
| Memory / retrieval | Conversation state, memory and knowledge retrieval | Pending design |
| Security | Identity, access policy, secrets, audit and rate controls | Partial foundation exists; hardening pending |
| Observability | Logs, metrics, traces and alerts | Planned |
| Deployment | Reproducible environments and release process | Pending |

## 4. Verified repository baseline

The current repository contains a Python/FastAPI application with:
- tenant and tenant API-key data models;
- admin-protected tenant provisioning and activation/deactivation;
- hashed tenant API-key storage, key listing, creation and revocation;
- tenant-scoped usage summaries and request-recording middleware;
- optional Redis-backed per-tenant fixed-window rate limiting;
- automated test files and a GitHub Actions test workflow.

These are existing foundations, not proof of production readiness. Their behavior and test coverage must be audited before extension.

## 5. Technology inventory

| Area | Current repository evidence | Decision |
|---|---|---|
| Language | Python | Existing |
| API framework | FastAPI | Existing |
| ORM | SQLAlchemy 2 | Existing |
| Local database | SQLite default | Development default only |
| Production database | PostgreSQL is configurable per README | Pending production decision |
| Rate limiting | Optional Redis integration | Existing; production configuration pending |
| AI model | None integrated in current documented baseline | Pending evaluation |
| Inference engine | None integrated in current documented baseline | Pending evaluation |
| Frontend | No frontend framework established in the inspected baseline | Pending |
| Deployment target | Not established | Pending |

## 6. Key interfaces to define before implementation

- Model provider interface: generate response, stream response, report model metadata and normalized errors.
- Inference runtime interface: load/unload model, readiness, resource limits and health.
- API contracts: versioning, authentication, validation, error envelope and request IDs.
- Persistence contracts: migrations, transaction boundaries and data ownership.
- Memory contracts: read/write scope, retention, deletion and tenant isolation.

These are design targets, not implemented interfaces.

## 7. Decisions still required

See [Decision Log](DECISIONS.md). In particular: target hardware/deployment, model family and license, inference engine, production database, memory design, frontend framework, and operational requirements.
