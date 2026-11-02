import httpx
import pytest

from app.providers.cloudflare_workers_ai import (
    CloudflareWorkersAIClient,
    ProviderConfigurationError,
    ProviderRequestError,
)


@pytest.mark.asyncio
async def test_cloudflare_adapter_sends_authenticated_model_request(monkeypatch):
    captured = {}

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"success": True, "result": {"response": "Namaste from BIRAJ AI"}}

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, url, headers, json):
            captured.update(url=url, headers=headers, payload=json)
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    client = CloudflareWorkersAIClient(
        account_id="account-test",
        api_token="token-test",
        model="@cf/zai-org/glm-4.7-flash",
    )

    answer = await client.generate(
        [{"role": "user", "content": "Namaste"}],
        max_tokens=123,
    )

    assert answer == "Namaste from BIRAJ AI"
    assert captured["url"].endswith(
        "/accounts/account-test/ai/run/@cf/zai-org/glm-4.7-flash"
    )
    assert captured["headers"]["Authorization"] == "Bearer token-test"
    assert captured["payload"]["messages"] == [
        {"role": "user", "content": "Namaste"}
    ]
    assert captured["payload"]["max_tokens"] == 123


@pytest.mark.asyncio
async def test_cloudflare_adapter_requires_credentials():
    client = CloudflareWorkersAIClient(account_id="", api_token="")
    with pytest.raises(ProviderConfigurationError):
        await client.generate([{"role": "user", "content": "Hello"}])


@pytest.mark.asyncio
async def test_cloudflare_adapter_rejects_non_cloudflare_model():
    client = CloudflareWorkersAIClient(
        account_id="account-test",
        api_token="token-test",
        model="openai/example-model",
    )
    with pytest.raises(ProviderConfigurationError):
        await client.generate([{"role": "user", "content": "Hello"}])


@pytest.mark.asyncio
async def test_cloudflare_adapter_stops_on_http_error_without_fallback(monkeypatch):
    class FakeResponse:
        status_code = 403

        def raise_for_status(self):
            request = httpx.Request("POST", "https://api.cloudflare.com/test")
            response = httpx.Response(403, request=request)
            raise httpx.HTTPStatusError("forbidden", request=request, response=response)

    class FakeAsyncClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, traceback):
            return False

        async def post(self, *args, **kwargs):
            return FakeResponse()

    monkeypatch.setattr(httpx, "AsyncClient", FakeAsyncClient)
    client = CloudflareWorkersAIClient(
        account_id="account-test",
        api_token="token-test",
    )
    with pytest.raises(ProviderRequestError, match="HTTP 403"):
        await client.generate([{"role": "user", "content": "Hello"}])
