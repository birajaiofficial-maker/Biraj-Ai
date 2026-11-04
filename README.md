# BIRAJ AI

BIRAJ AI is being built as a modular AI platform using an **open-weight model operated in infrastructure controlled by BIRAJ AI**. The immediate goal is to build and verify the reusable core platform before expanding end-user products.

## Current status

- **Current branch:** `work/open-weight-core`
- **Current phase:** Phase 0 — migration to the open-weight/self-hosted development baseline
- **Core platform:** Not complete
- **Exact model:** Not selected
- **Inference runtime:** Not selected
- **Production deployment:** Not configured

Existing Python/FastAPI backend code is a starting point, not a production-ready system. The prior Cloudflare Workers AI proposal and the separate Ollama/Qwen experiment remain unmerged and are not automatically part of this baseline.

## Non-negotiable runtime boundary

- Do not use OpenAI or Google Gemini as BIRAJ AI runtime model providers.
- Do not use Cloudflare Workers AI or another hosted model API as the production inference dependency.
- Prefer open-weight models with licenses that permit the intended use, after license review.
- Run inference locally or on infrastructure explicitly controlled and approved by BIRAJ AI.
- ChatGPT may assist with development, code review, debugging and documentation. It is not a runtime dependency of BIRAJ AI.
- No paid GPU, cloud inference, hosted model API, subscription or vendor commitment without explicit approval.
- Do not assume that "open source" means unrestricted commercial use; verify the exact model and code licenses.

## Development principles

1. Inspect before changing. Preserve useful existing work and history.
2. Keep one authoritative task record in the Notion Development Task Tracker.
3. Every code change links to one Task ID and a GitHub branch/PR.
4. Build one module at a time with explicit acceptance criteria.
5. Test changes and record actual results; never invent passing tests.
6. Keep model, inference runtime and application logic behind replaceable interfaces.
7. Do not mark a module complete until its tests, security checks and documentation gates pass.

## Documentation

See [technical documentation](docs/README.md): architecture, development plan, decision log, model/runtime evaluation, module register, workflow, testing, security and branch register.

Notion tracks task status, milestones, approvals and progress. GitHub tracks source code, commits, pull requests, tests and releases. Link records rather than copying the same task into multiple trackers.

## Existing foundation (requires audit)

The existing repository has an early FastAPI/Python backend, tenant/API-key management, SQLAlchemy persistence, usage tracking, Redis rate limiting and tests. Tenant-name normalization and a bounded process-local rate-limit fallback during Redis outages are now included with regression coverage. These changes have not yet been executed in tests on this branch; treat every component as unverified until tested.

## Local development

Python 3.11+ is the current backend baseline.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set local development secrets only in `.env` and never commit them. Use the startup command documented by the active application configuration.

## Current migration branch

This branch is a clean migration baseline created from `main`. It does not merge or close the older draft PRs. See [branch register](docs/BRANCHES.md) for their status and safe disposition.

## Important

This is an early development project, not a production-ready platform. Model choice, hardware, database, memory design, frontend and deployment remain subject to evaluation and approval.
