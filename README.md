# BIRAJ AI

BIRAJ AI is being developed as a modular AI platform. The current engineering objective is to complete and verify the reusable core platform before expanding end-user services.

## Project status

**Current phase:** Core platform foundation and Cloudflare Workers AI adapter integration.  
**Core platform:** Not complete.  
**Runtime provider:** Cloudflare Workers AI only (approved).  
**Inference default:** Disabled until account credentials, model access, quota and billing safeguards are verified.

This repository contains an early Python/FastAPI foundation for API access, tenant management, API-key handling, usage recording and optional Redis-backed rate limiting. It also contains a Cloudflare Workers AI REST adapter and an authenticated AI chat route. These are implementation foundations, not proof of production readiness.

## Development principles

- Build and test the core platform one module at a time.
- Keep modules replaceable and interfaces documented.
- Cloudflare Workers AI is the only approved BIRAJ AI runtime provider at this stage.
- Do not add OpenAI, Google Gemini, Groq, Ollama or another runtime provider.
- ChatGPT is used as an external development assistant; it is not a BIRAJ AI runtime dependency.
- Do not enable paid billing or paid usage without explicit user approval.
- If inference is disabled, credentials are missing, or Cloudflare rejects a request because of quota, permissions or availability, stop safely. Do not silently switch providers or upgrade billing.
- Do not add end-user service expansion, pricing, subscriptions or promotion planning before core completion.
- Record confirmed decisions and mark unresolved choices as pending.

## Documentation

The authoritative technical documentation lives in docs/:

- Architecture
- Development plan
- Decision log
- Testing strategy
- Module register
- Branch register

GitHub is the source of truth for code, branches, commits and CI. Notion tracks project decisions, tasks and meaningful changes.

## Existing foundation (not production-ready)

- FastAPI application and API routes
- SQLAlchemy data models
- Tenant provisioning and tenant API-key lifecycle
- Tenant-scoped usage recording
- Shared Redis-backed rate limiting with a bounded per-process emergency fallback when Redis is unavailable
- Cloudflare Workers AI REST adapter (app/providers/cloudflare_workers_ai.py)
- Authenticated AI status and chat routes (app/ai.py)
- Adapter and API tests
- GitHub Actions test workflow

## Local development

The existing application uses Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set a long, random BIRAJ_ADMIN_KEY in .env, then run:

```bash
uvicorn app.main:app --reload --env-file .env
```

Open http://127.0.0.1:8000/docs.

Cloudflare inference remains disabled by default. Never commit real API keys, passwords or production secrets. Do not enable inference until the account's free quota, model access and billing behavior have been checked.

## Important

This repository is an early development foundation, not a production-ready platform. Follow the development plan and testing strategy before claiming completion or deploying for real users.
