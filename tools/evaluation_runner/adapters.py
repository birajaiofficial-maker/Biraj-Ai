"""Provider-neutral local model adapter contract and offline test double.

No network, subprocess, model download, or inference runtime is used here.
Future runtime adapters must implement the same ModelAdapter protocol.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class GenerationRequest:
    """One generation request independent of the selected runtime."""

    prompt: str
    system_prompt: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_new_tokens: int | None = None
    stop: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class GenerationResult:
    """Normalized result returned by any compatible adapter."""

    text: str
    model_id: str
    runtime_name: str
    runtime_version: str | None = None
    prompt_tokens: int | None = None
    output_tokens: int | None = None
    time_to_first_token_ms: float | None = None
    generation_duration_ms: float | None = None
    tokens_per_second: float | None = None
    finish_reason: str | None = None
    raw_metadata: dict[str, Any] = field(default_factory=dict)


class AdapterError(RuntimeError):
    """Base class for normalized adapter failures."""


class AdapterUnavailableError(AdapterError):
    """Raised when a runtime is not reachable or not configured."""


class AdapterTimeoutError(AdapterError):
    """Raised when a runtime exceeds its configured timeout."""


class AdapterResponseError(AdapterError):
    """Raised when a runtime response cannot be normalized."""


class ModelAdapter(Protocol):
    """Contract all future local runtime adapters must implement."""

    @property
    def runtime_name(self) -> str:
        """Stable runtime identifier, e.g. 'ollama' or 'llama.cpp'."""

    def health(self) -> bool:
        """Return True only when the runtime can accept inference requests."""

    def model_info(self) -> dict[str, Any]:
        """Return normalized model identity and runtime metadata."""

    def generate(self, request: GenerationRequest) -> GenerationResult:
        """Generate one response or raise a normalized AdapterError."""


class MockAdapter:
    """Deterministic offline adapter for tests and interface validation."""

    runtime_name = "mock/offline"

    def __init__(
        self,
        *,
        model_id: str = "biraj-mock-model",
        response_text: str = "BIRAJ AI mock response",
        available: bool = True,
    ) -> None:
        self._model_id = model_id
        self._response_text = response_text
        self._available = available
        self.requests: list[GenerationRequest] = []

    def health(self) -> bool:
        return self._available

    def model_info(self) -> dict[str, Any]:
        return {
            "model_id": self._model_id,
            "runtime_name": self.runtime_name,
            "runtime_version": None,
            "mode": "mock-only",
        }

    def generate(self, request: GenerationRequest) -> GenerationResult:
        if not self._available:
            raise AdapterUnavailableError("Mock adapter is marked unavailable")
        if not request.prompt.strip():
            raise AdapterResponseError("Prompt must not be empty")

        self.requests.append(request)
        return GenerationResult(
            text=self._response_text,
            model_id=self._model_id,
            runtime_name=self.runtime_name,
            finish_reason="mock_complete",
            raw_metadata={"mock": True},
        )
