# BIRAJ AI — Core Development Plan

**Current phase:** Phase 0 — migration to the open-weight/self-hosted baseline  
**Overall status:** Core platform incomplete  
**Model/runtime:** Not selected  
**Production deployment:** Not configured

## Working method

For each module: inspect existing code → define requirements → record task and acceptance criteria → design interface → implement the smallest coherent change → test → security review → document → update Notion and GitHub. Integrate modules only after individual gates pass.

## Phases

| Phase | Scope | Exit gate | Status |
|---|---|---|---|
| 0 | Migrate documentation, branches and project records to the new runtime boundary; preserve old work | No contradictory active architecture; old PRs/branches disposition recorded | In progress |
| 1 | Requirements and hardware constraints | Functional/non-functional requirements, usage assumptions and hardware profile recorded | Planned |
| 2 | Model evaluation | Candidate licenses, Hindi/English quality, reasoning/coding, context and resource benchmarks compared | Pending |
| 3 | Inference runtime | Runtime selected; local serving, API contract, health/readiness and failure behavior verified | Pending |
| 4 | Backend/API foundation | Versioned API, auth, validation, error handling and internal model adapter pass tests | Partial foundation |
| 5 | Data and migrations | Database choice, schema, Alembic migration and backup/restore verified | Partial foundation |
| 6 | Conversation, memory and retrieval | Scope, storage, retrieval, retention, deletion and tenant isolation tests pass | Planned |
| 7 | Security and access control | Threat review, authz, secrets, tenant isolation, audit and abuse controls pass | Partial foundation |
| 8 | Frontend | UI integrates with documented API and handles auth/errors safely | Planned |
| 9 | Integration and quality | Unit, integration, security, load and end-to-end gates pass | Planned |
| 10 | Deployment readiness | Reproducible self-hosted deployment, monitoring, backup/restore and rollback verified | Planned |

## Phase 0 — immediate sequence

1. Establish this branch as the new migration baseline.
2. Replace hosted-provider architecture references with the self-hosted open-weight boundary.
3. Keep PR #1 (Ollama/Qwen experiment) unmerged pending model/runtime evaluation.
4. Keep PR #4 (Cloudflare provider change) unmerged and exclude it from the new baseline.
5. Reconcile the branch register and avoid deleting historical branches until unique commits are accounted for.
6. Align Notion dashboard, task tracker and decision/change records with this branch.
7. Review the current backend on this branch and identify which safe non-provider changes can be ported independently. (Tenant-name normalization and Redis outage fallback are present; the fallback is explicitly process-local and not a distributed quota. Ollama and Cloudflare provider implementations remain excluded.)

## Explicitly out of scope until core completion

Pricing, subscriptions, monetization, marketing, customer-specific deployments, paid GPU/cloud commitments and hosted model APIs.

## Definition of core completion

Core is complete only when a licensed open-weight model runs through the selected self-hosted inference runtime; API, orchestration, data, memory, security and UI are integrated; automated tests pass; operational and security checks are documented; and self-hosted deployment, backup/restore and rollback are verified.
