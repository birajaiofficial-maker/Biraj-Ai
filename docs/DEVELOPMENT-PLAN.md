# BIRAJ AI — Core Development Plan

**Current phase:** Phase 0 — repository audit and project baseline  
**Overall status:** Core platform not complete. No end-user service expansion in this phase.

## Working method

Build one component at a time. For each component: define requirements → inspect dependencies → design interface → implement → test → review security → document → mark complete. Integrate components only after their individual gates pass, then run system-level tests.

## Phases

| Phase | Scope | Exit gate | Status |
|---|---|---|---|
| 0 | Repository audit, baseline, documentation and duplicate-work controls | Existing code and gaps are inventoried; plan approved | In progress |
| 1 | Requirements and constraints | Functional/non-functional requirements and hardware assumptions recorded | Planned |
| 2 | Model evaluation and selection | Candidate benchmark, license review, language/quality and resource evaluation documented | Pending decision |
| 3 | Inference runtime / engine | Runtime selected and model can be served with health/readiness checks | Planned |
| 4 | Backend and API foundation | Stable versioned API, validation, error handling and model adapter | Existing backend requires audit and extension |
| 5 | Data layer and migrations | Production database choice, schema and migration workflow verified | Partial foundation |
| 6 | Memory and retrieval foundation | Scope, persistence, retrieval and retention tests pass | Planned |
| 7 | Security and access control | Threat review, auth, authorization, secret handling, tenant isolation and audit requirements pass | Partial foundation |
| 8 | Frontend foundation | UI connects to documented API and handles errors/auth safely | Planned |
| 9 | Integration and quality | Unit, integration, security and end-to-end gates pass | Planned |
| 10 | Deployment readiness | Reproducible deployment, backup/restore, monitoring and rollback verified | Planned |

Phases may be refined after the audit, but changes must be recorded in the decision log. Do not skip a phase's exit gate.

## First work items

1. Audit existing Python modules, API routes, models, security logic and tests.
2. Run the current automated test suite and record the actual result.
3. Identify security and architecture gaps without rewriting working code unnecessarily.
4. Capture functional and non-functional requirements.
5. Evaluate model candidates against those requirements before selecting a model or engine.

## Explicitly out of scope until core completion

- Customer-facing service catalog expansion and vertical-specific workflows.
- Pricing, subscriptions, monetization, marketing and promotion planning.
- Production launch claims before deployment and security gates pass.

## Completion definition

The core platform is complete only when the chosen model runs through the selected inference runtime; the backend, API, data, memory, security and frontend are integrated; automated tests pass; operational and security checks are documented; and deployment/rollback has been verified.
