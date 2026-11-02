import os

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models import Tenant
from app.providers.cloudflare_workers_ai import (
    CloudflareWorkersAIClient,
    ProviderConfigurationError,
    ProviderRequestError,
)
from app.security import get_current_tenant

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

DEFAULT_SYSTEM_PROMPT = (
    "You are BIRAJ AI, a helpful and honest AI assistant. "
    "Give clear, practical answers and respond in the user's language when possible. "
    "If you are unsure, say so rather than inventing facts."
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


@router.get("/status")
def ai_status(tenant: Tenant = Depends(get_current_tenant)):
    """Report safe runtime configuration without exposing credentials."""
    enabled = os.getenv("BIRAJ_AI_ENABLED", "false").lower() == "true"
    return {
        "service": "BIRAJ AI",
        "provider": "cloudflare_workers_ai",
        "enabled": enabled,
        "model": os.getenv("BIRAJ_AI_MODEL", CloudflareWorkersAIClient().model),
        "tenant": "active",
    }


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    tenant: Tenant = Depends(get_current_tenant),
):
    """Generate one response using the only approved runtime provider."""
    if os.getenv("BIRAJ_AI_ENABLED", "false").lower() != "true":
        raise HTTPException(
            status_code=503,
            detail="BIRAJ AI inference is disabled until Cloudflare configuration is verified.",
        )

    system_prompt = os.getenv("BIRAJ_AI_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)
    max_tokens = max(1, min(int(os.getenv("BIRAJ_AI_MAX_OUTPUT_TOKENS", "512")), 2048))
    client = CloudflareWorkersAIClient()

    try:
        answer = await client.generate(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": payload.message},
            ],
            max_tokens=max_tokens,
        )
    except ProviderConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ProviderRequestError as exc:
        # Upstream quota/permission/network failures stop here. No provider
        # fallback, automatic retry, or paid-plan switch is attempted.
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        "answer": answer,
        "provider": "cloudflare_workers_ai",
        "model": client.model,
    }
