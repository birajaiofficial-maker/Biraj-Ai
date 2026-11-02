# BIRAJ AI

BIRAJ AI is being developed as a modular AI platform. The current engineering objective is to complete and verify the reusable core platform before expanding end-user services.

## Project status

**Current phase:** Phase 0 — repository audit and project baseline.  
**Core platform:** Not complete.  
**Runtime AI model and inference engine:** Not selected or integrated.

This repository already contains an early Python/FastAPI foundation for API access, tenant management, API-key handling, usage recording and optional Redis-backed rate limiting. Existing code is a starting point and must be audited and tested; its presence does not mean it is production-ready.

## Development principles

- Build and test the core platform one module at a time.
- Keep modules replaceable and interfaces documented.
- Do not use OpenAI or Google Gemini as BIRAJ AI runtime model providers.
- ChatGPT is used as an external development assistant; it is not a BIRAJ AI runtime dependency.
- Do not add end-user service expansion, pricing, subscriptions or promotion planning before core completion.
- Record confirmed decisions and mark unresolved choices as pending.

## Documentation

The authoritative technical documentation lives in [`docs/`](docs/README.md):

- [Architecture](docs/ARCHITECTURE.md)
- [Development plan](docs/DEVELOPMENT-PLAN.md)
- [Decision log](docs/DECISIONS.md)
- [Testing strategy](docs/TESTING.md)
- [Module register](docs/modules/README.md)

GitHub Issues track individual tasks and bugs. The documentation is the source of truth for architecture, decisions and project status.

## Existing foundation (to be audited)

- FastAPI application and API routes
- SQLAlchemy data models
- Tenant provisioning and tenant API-key lifecycle
- Tenant-scoped usage recording
- Optional Redis-backed rate limiting
- Automated test files and GitHub Actions workflow

See the documentation before making architectural changes. Do not assume an existing component is production-ready until its tests and security review pass.

## Local development

The existing application uses Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set a long, random `BIRAJ_ADMIN_KEY` in `.env`, then run:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

Never commit real API keys, passwords or production secrets.

## Important

This repository is an early development foundation, not a production-ready platform. Follow [the development plan](docs/DEVELOPMENT-PLAN.md) and [testing strategy](docs/TESTING.md) before claiming completion or deploying for real users.
