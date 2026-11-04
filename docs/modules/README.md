# BIRAJ AI — Module Register

This is the single module index. Each module receives one authoritative specification only when requirements are ready. Do not duplicate full specifications across documents.

| Module | Responsibility | Existing evidence | Status | Next action |
|---|---|---|---|---|
| API / backend | HTTP boundary, auth, validation, request lifecycle | FastAPI application and tenant routes | Partial; audit required | Stabilize API contract and configuration |
| Tenant / identity | Tenant records, API keys, isolation and permissions | SQLAlchemy models and routes | Partial; security review required | Verify authorization and isolation |
| Configuration | Environment parsing, validation and secret boundaries | Environment variables used in app | Incomplete | Centralize validated settings |
| Data / migrations | Persistence, schema evolution and transactions | SQLAlchemy models; create_all foundation | Partial | Add and test migrations |
| Rate limiting | Per-tenant abuse protection | Redis integration and local fallback in experimental branch | Needs reconciliation | Decide safe behavior and test multi-instance limits |
| Model adapter | Internal generate/stream/model-info interface | Competing unmerged Ollama and Cloudflare experiments | Not accepted | Define provider-neutral internal contract |
| Inference runtime | Load and serve selected open-weight model | Ollama experiment in PR #1 only | Not selected | Evaluate models/runtime/hardware |
| Orchestration | Prompt assembly, conversation policy and tool boundary | Minimal system prompt experiment | Not implemented as full module | Define requirements |
| Conversation / memory | Conversation persistence and memory lifecycle | Not established | Planned | Define retention and tenant boundaries |
| Retrieval / knowledge | Embeddings, indexing and retrieval | Not established | Planned | Define use cases and evaluation |
| Security / audit | Authz, secrets, audit logs, threat controls | Partial auth and key hashing | Partial | Threat model and hardening |
| Observability | Logs, metrics, tracing, health/readiness | Basic logging and health endpoint | Incomplete | Define operational signals |
| Frontend | User interface | No verified frontend baseline | Not established | Requirements first |
| Deployment / operations | Self-hosted release, backup, monitoring and rollback | Not established | Planned | Define after runtime selection |

## Module specification template

Every module spec must include purpose/non-goals, interface, dependencies, data/security implications, failure behavior, observability, tests, acceptance criteria, status/evidence and open questions.
