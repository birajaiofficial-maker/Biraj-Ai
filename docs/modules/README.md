# Module Register

This is the index only. Each module gets one authoritative specification under this folder when its requirements are ready. Avoid duplicating full specifications in other documents.

| Module | Responsibility | Current status | Next action |
|---|---|---|---|
| API / backend | HTTP boundary, orchestration and request lifecycle | Partial implementation | Audit routes and contracts |
| Tenant and access foundation | Tenant records, API keys, tenant scoping | Implemented baseline; verification pending | Review isolation and key lifecycle |
| Database | Persistence and schema evolution | Basic SQLAlchemy models | Audit schema and add migration plan |
| Rate limiting | Shared tenant request limits | Optional Redis implementation | Test failure modes and production behavior |
| Model adapter | Provider-neutral application interface | Not implemented | Define after model/runtime evaluation |
| Model runtime | Load and serve selected model | Not implemented | Pending model and hardware decisions |
| Memory / retrieval | Conversation state and knowledge retrieval | Not implemented | Define requirements and data boundaries |
| Security / audit | Identity, permissions, secrets, auditability | Partial foundation | Threat-model and gap assessment |
| Frontend | User interface | Not established | Define requirements after API baseline |
| Observability / deployment | Logs, metrics, health, release and rollback | Not established | Define operational requirements |

## Module specification template

Each module specification should contain:
- Purpose and non-goals
- Inputs, outputs and API/interface contract
- Dependencies and ownership boundaries
- Data model and security considerations
- Failure behavior and observability
- Test plan and acceptance criteria
- Status, open questions and decision-log links
