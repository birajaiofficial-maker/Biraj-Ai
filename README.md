# BIRAJ AI

BIRAJ AI is an API-first, multi-tenant AI customer support and business automation platform.

## MVP scope

- Customer Support API foundation
- Knowledge Base integration foundation
- Multilingual support foundation
- Health and service-discovery endpoints

The repository currently contains the initial backend scaffold. AI provider integration, tenant authentication, persistent storage, retrieval, and business integrations are not yet implemented.

## Technology

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

On Android/Termux, open `http://127.0.0.1:8000/docs` in your browser after starting the server.

## Endpoints

- `GET /` — API information
- `GET /health` — health check
- `GET /api/v1/services` — MVP service catalogue

## Configuration

Copy `.env.example` to `.env` before adding local configuration. Never commit API keys, passwords, or production secrets.

## Project status

Early development. Do not use in production until authentication, tenant isolation, rate limiting, audit logging, and data protection are implemented and tested.
