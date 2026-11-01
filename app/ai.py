import os

import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.models import Tenant
from app.security import get_current_tenant

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

DEFAULT_OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:0.5b-instruct"
DEFAULT_SYSTEM_PROMPT = (
    "You are BIRAJ AI, a helpful and honest AI assistant. "
    "Give clear, practical answers. Match the user's language when possible. "
    "If you are unsure, say so rather than inventing facts. "
    "Do not claim that the model was trained from scratch by BIRAJ AI."
)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)


@router.get("/status")
def ai_status(tenant: Tenant = Depends(get_current_tenant)):
    """Report configured local model settings without exposing internal URLs."""
    return {
        "service": "BIRAJ AI local model runtime",
        "provider": "ollama",
        "model": os.getenv("BIRAJ_AI_MODEL", DEFAULT_MODEL),
        "connection": "not_checked",
        "tenant": "active",
    }


@router.post("/chat")
async def chat(
    payload: ChatRequest,
    tenant: Tenant = Depends(get_current_tenant),
):
    """Send one message to the self-hosted Ollama runtime; no external AI API."""
    base_url = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_URL).rstrip("/")
    model = os.getenv("BIRAJ_AI_MODEL", DEFAULT_MODEL)
    system_prompt = os.getenv("BIRAJ_AI_SYSTEM_PROMPT", DEFAULT_SYSTEM_PROMPT)

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0, connect=5.0)) as client:
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": payload.message},
                    ],
                    "stream": False,
                },
            )
            response.raise_for_status()
            result = response.json()
            answer = result.get("message", {}).get("content")
            if not isinstance(answer, str) or not answer.strip():
                raise ValueError("The local model returned an empty response.")
            return {
                "answer": answer,
                "model": model,
                "provider": "ollama",
            }
    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=503,
            detail="Local AI runtime is unavailable. Start Ollama and load the configured model.",
        ) from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(
            status_code=504,
            detail="The local AI runtime took too long to respond.",
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail="The local AI runtime returned an error.",
        ) from exc
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=502,
            detail="The local AI runtime returned an invalid response.",
        ) from exc
