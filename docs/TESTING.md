# BIRAJ AI — Testing Strategy

**Status:** Test policy baseline. Actual pass/fail state must come from executed test runs.

## Test levels

1. Unit: configuration, validation, orchestration, model adapter normalization and business rules.
2. API: routes, schemas, auth, status codes, request IDs and error envelopes.
3. Integration: database/migrations, Redis, local inference service, memory and retrieval.
4. Security: tenant isolation, authorization bypass, API-key lifecycle, secret leakage, rate limits and prompt/data boundaries.
5. Model quality: reproducible Hindi/English prompts, instruction following, reasoning/coding and hallucination review.
6. End-to-end: client/API → orchestration → self-hosted inference → persistence → response.
7. Operations: startup/readiness, dependency outages, shutdown, backup/restore, monitoring and rollback.
8. Performance: latency, throughput, concurrency, memory and context-window behavior on declared hardware.

## Required gates

- Every bug fix includes regression coverage where practical.
- Every new module tests success, invalid input, failure and permission boundaries.
- No real secrets in source, fixtures, logs or documentation.
- Tests are repeatable and run in CI.
- Local inference integration tests may use deterministic fakes for CI; live model tests must be clearly separated and explicitly run on configured hardware.
- A passing mock test does not prove a real model server is reachable or performant.
- Record command, environment, commit, date and result.
- Never claim tests passed unless they were actually executed.

## Current baseline evidence

The repository contains API and tenant-isolation tests and a GitHub Actions workflow. Regression coverage includes tenant-name normalization and bounded local rate limiting during Redis outages. GitHub Actions run [#33](https://github.com/birajaiofficial-maker/Biraj-Ai/actions/runs/41746723627) on `work/open-weight-core` completed successfully: `pytest -q` reported **7 passed, 3 warnings** (2026-11-04). Warnings include deprecated FastAPI `on_event` lifecycle usage and the Starlette/httpx TestClient integration; they are not test failures and should be addressed in a separate cleanup task.

A module is complete only when its acceptance tests pass, security boundaries are checked, operational failure behavior is documented and relevant technical/Notion records are updated.
