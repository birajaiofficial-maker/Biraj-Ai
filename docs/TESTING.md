# BIRAJ AI — Testing Strategy

**Status:** Strategy baseline. Actual pass/fail status must come from executed test runs, not assumptions.

## Test levels

1. **Unit tests** — isolated functions, validation, model adapters and business rules.
2. **API tests** — routes, schemas, status codes, authentication and error responses.
3. **Integration tests** — database, migrations, Redis (when enabled), model runtime and memory boundaries.
4. **Security tests** — authorization bypass, tenant isolation, key handling, rate limits, input validation and secret leakage.
5. **End-to-end tests** — complete request flow from client/API to model response and persistence.
6. **Operational tests** — startup/readiness, shutdown, backup/restore, monitoring and deployment rollback.

## Required gates

- Every bug fix includes a regression test where practical.
- New modules include tests for success, invalid input, failure and permission boundaries.
- No secrets or real credentials in source, fixtures, logs or documentation.
- Tests must be repeatable and run in CI.
- A module is not complete solely because its code exists; its documented acceptance tests must pass.
- Record command, environment, date/commit and result for meaningful test runs.

## Current repository evidence

The repository contains `tests/test_api.py`, `tests/test_tenant_isolation.py` and `.github/workflows/tests.yml`.

### Verified CI run

- Commit: `d8778c9fba57ed389026d2d00f7958fdd61594b8` (documentation PR head at the time of the run)
- Workflow: **BIRAJ AI tests**, GitHub Actions run [#10](https://github.com/birajaiofficial-maker/Biraj-Ai/actions/runs/41380444571)
- Environment: GitHub-hosted Ubuntu runner, Python 3.11
- Command: `pytest -q`
- Result: **5 passed**, 3 warnings; job completed successfully.
- Warnings observed: Starlette's `httpx` TestClient deprecation, FastAPI `on_event` deprecation, and runner/action Node.js 20 deprecation notice.

This verifies the current five-test baseline at that commit only. It is not a production-readiness or comprehensive security assessment. Re-run CI after subsequent code changes.
