# BIRAJ AI — System Architecture

**Status:** Target architecture baseline for the open-weight/self-hosted direction. This is a design target, not a statement that all layers are implemented.

## 1. Product and runtime boundary

BIRAJ AI will use an eligible open-weight model served by an inference runtime operated on local or explicitly approved BIRAJ-controlled infrastructure.

Not runtime providers:
- OpenAI API
- Google Gemini API
- Cloudflare Workers AI
- Other hosted third-party model APIs

ChatGPT can assist the development process but must not be called by the deployed BIRAJ AI application.

The exact model, inference engine, hardware and deployment location remain pending evaluation. Ollama, vLLM and llama.cpp are candidates to assess, not approved production choices.

## 2. Architecture principles

- Self-hosted inference: model weights and inference execute in an environment controlled by BIRAJ AI.
- Replaceable runtime: backend logic depends on a documented internal model interface, not a specific model vendor.
- Open-weight license review: review the exact model license and redistribution/commercial-use restrictions before adoption.
- Local-first cost control: support local development and avoid paid services by default.
- Modular design: one responsibility per module and one authoritative implementation.
- API-first: stable, versioned API contracts.
- Secure by default: authentication, authorization, tenant isolation, secret handling and audit records.
- Graceful degradation: distinguish liveness, readiness and dependency failures; do not silently switch to hosted providers.
- Evidence-based status: implementation and test status must reflect observed repository/CI evidence.

## 3. Logical layers

| Layer | Responsibility | Current status |
|---|---|---|
| Client / UI | User-facing interface | Not established |
| API boundary | Versioned requests, auth, validation, errors | Early FastAPI foundation |
| Backend orchestration | Conversation/request coordination, tenant policy | Partial foundation |
| Model adapter | Internal provider-neutral generation interface | To design |
| Inference service | Serve selected open-weight model | Not selected or integrated in this baseline |
| Model artifacts | Downloaded/managed weights and tokenizer | Not selected |
| Data layer | Users, tenants, conversations, usage, settings | Basic SQLAlchemy foundation; migration work pending |
| Memory / retrieval | Conversation history and knowledge retrieval | Not designed |
| Security / governance | Auth, permissions, secrets, isolation, audit | Partial foundation; audit pending |
| Observability | Logs, metrics, traces and health | Incomplete |
| Deployment / operations | Reproducible runtime, backup, rollback | Not established |

## 4. Target request flow

1. Client sends a request to the BIRAJ AI API.
2. API authenticates the user/tenant and validates input.
3. Backend applies authorization, request limits and conversation policy.
4. Orchestrator assembles permitted context and prompt messages.
5. Internal model adapter sends the request to the self-hosted inference service over a private/local interface.
6. Adapter normalizes response, errors, model metadata and streaming behavior.
7. Backend records permitted usage/audit metadata and persists conversation state according to retention policy.
8. API returns the response to the client.

No hosted model API fallback is allowed. If the self-hosted inference service is unavailable, return a clear service-unavailable response and preserve diagnostic evidence without leaking secrets.

## 5. Separation of concerns

- Application API: authentication, request validation, tenant policy and API contracts.
- Orchestration: prompt assembly, conversation flow, tool policy and context selection.
- Model adapter: stable internal interface for generate/stream/health/model metadata.
- Inference runtime: model loading, token generation, batching and hardware utilization.
- Memory/retrieval: persistence, embeddings/indexes, retrieval and deletion policy.
- Operations: configuration, health/readiness, metrics, backup, release and rollback.

Do not mix provider-specific HTTP calls into route handlers.

## 6. Technology inventory

| Area | Existing evidence | Target / decision |
|---|---|---|
| Language | Python | Retain unless evidence requires change |
| API | FastAPI | Existing; audit and harden |
| ORM | SQLAlchemy | Existing; audit and migrate |
| Local database | SQLite default in current foundation | Development only unless separately approved |
| Production database | Not confirmed | Evaluate PostgreSQL and alternatives |
| Rate limiting | Redis integration in existing code | Retain only after resilience/security tests |
| Model family | No final selection | Evaluate open-weight candidates |
| Inference runtime | No final selection | Evaluate Ollama, vLLM, llama.cpp and fit-for-hardware alternatives |
| Frontend | Not established | Requirements first |
| Deployment | Not established | Local-first; later evaluate self-hosted deployment |

## 7. Decisions required before production inference

Exact model/license, runtime, hardware, context/performance target, artifact integrity, API streaming contract, memory/privacy policy, monitoring and recovery must be evaluated. No model or runtime is production-approved until evidence and explicit acceptance exist.
