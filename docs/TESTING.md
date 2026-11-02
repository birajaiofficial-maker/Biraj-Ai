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

### Verified CI runs

- **Latest documentation PR head:** commit `d9f69af98e428a552483a13fd7f74c3afafca358`; GitHub Actions workflow **BIRAJ AI tests**, [run #13](https://github.com/birajaiofficial-maker/Biraj-Ai/actions/runs/41400539969); GitHub-hosted Ubuntu runner, Python 3.11; command `pytest -q`; result **5 passed, 3 warnings**; job completed successfully on 2026-11-02.
- **Earlier documentation PR run:** commit `431059bc3e2ba4db1828760cf7206ebff48f2f43`; [run #12](https://github.com/birajaiofficial-maker/Biraj-Ai/actions/runs/41400445103); **5 passed, 3 warnings**.
- **Experimental local-runtime PR:** commit `99ac4a58c048e2f52bd8a1dbafdfe38764bd8df6`; [run #9](https://github.com/birajaiofficial-maker/Biraj-Ai/actions/runs/41274195738); workflow completed successfully. Passing CI verifies the automated test suite only; it does not approve the model/runtime choice or prove live Ollama connectivity.

Warnings observed on the latest documentation run: Starlette's `httpx` TestClient deprecation, FastAPI `on_event` deprecation, and GitHub runner/action Node.js 20 deprecation notice.

These are narrow baseline tests, not a production-readiness or comprehensive security assessment. Re-run CI after subsequent code changes.
