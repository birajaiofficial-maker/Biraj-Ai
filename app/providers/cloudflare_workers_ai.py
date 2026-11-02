import os

import httpx


DEFAULT_MODEL = "@cf/zai-org/glm-4.7-flash"
API_BASE_URL = "https://api.cloudflare.com/client/v4"


class ProviderConfigurationError(RuntimeError):
    """The Cloudflare Workers AI adapter is not configured."""


class ProviderRequestError(RuntimeError):
    """Cloudflare Workers AI rejected or failed a request."""


class CloudflareWorkersAIClient:
    """Small HTTP adapter for Cloudflare's account-scoped Workers AI REST API."""

    def __init__(self, account_id=None, api_token=None, model=None, timeout=45.0):
        self.account_id = account_id or os.getenv("CLOUDFLARE_ACCOUNT_ID")
        self.api_token = api_token or os.getenv("CLOUDFLARE_API_TOKEN")
        self.model = model or os.getenv("BIRAJ_AI_MODEL", DEFAULT_MODEL)
        self.timeout = timeout

    def _validate_config(self):
        if not self.account_id or not self.api_token:
            raise ProviderConfigurationError(
                "Cloudflare Workers AI credentials are not configured."
            )
        if not self.model.startswith("@cf/"):
            raise ProviderConfigurationError(
                "BIRAJ_AI_MODEL must identify a Cloudflare-hosted @cf/ model."
            )

    async def generate(self, messages, max_tokens=512):
        self._validate_config()
        url = (
            f"{API_BASE_URL}/accounts/{self.account_id}/ai/run/{self.model}"
        )
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messages": messages,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                body = response.json()
        except httpx.TimeoutException as exc:
            raise ProviderRequestError("Cloudflare Workers AI request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            # Do not retry or switch to another provider. In particular, quota,
            # plan and permission errors must stop safely without enabling billing.
            status_code = exc.response.status_code
            if status_code in (401, 403, 429):
                raise ProviderRequestError(
                    f"Cloudflare Workers AI rejected the request (HTTP {status_code}). "
                    "Check token permissions, model access and account quota."
                ) from exc
            raise ProviderRequestError(
                f"Cloudflare Workers AI returned HTTP {status_code}."
            ) from exc
        except httpx.RequestError as exc:
            raise ProviderRequestError(
                "Cloudflare Workers AI is temporarily unreachable."
            ) from exc
        except ValueError as exc:
            raise ProviderRequestError(
                "Cloudflare Workers AI returned invalid JSON."
            ) from exc

        if not isinstance(body, dict) or body.get("success") is False:
            raise ProviderRequestError("Cloudflare Workers AI reported an unsuccessful request.")

        result = body.get("result")
        answer = result.get("response") if isinstance(result, dict) else None
        if not isinstance(answer, str) or not answer.strip():
            raise ProviderRequestError(
                "Cloudflare Workers AI returned an unexpected or empty response."
            )
        return answer.strip()
