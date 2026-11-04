"""Provider-neutral local model adapter contract and offline test double.

No network, subprocess, model download, or inference runtime is used here.
Future runtime adapters must implement the same ModelAdapter protocol.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import math
from typing import Any, Protocol


MAX_PROMPT_CHARS = 100_000
MAX_SYSTEM_PROMPT_CHARS = 20_000
MAX_NEW_TOKENS = 8_192
MAX_STOP_SEQUENCES = 16
MAX_STOP_SEQUENCE_CHARS = 256


@dataclass(frozen=True)
class GenerationLimits:
    """Configurable, immutable resource bounds for one generation request."""

    max_prompt_chars: int = MAX_PROMPT_CHARS
    max_system_prompt_chars: int = MAX_SYSTEM_PROMPT_CHARS
    max_new_tokens: int = MAX_NEW_TOKENS
    max_stop_sequences: int = MAX_STOP_SEQUENCES
    max_stop_sequence_chars: int = MAX_STOP_SEQUENCE_CHARS

    def __post_init__(self) -> None:
        for name in (
            "max_prompt_chars",
            "max_system_prompt_chars",
            "max_new_tokens",
            "max_stop_sequences",
            "max_stop_sequence_chars",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise AdapterRequestError(f"{name} must be a positive integer")


def _is_finite_number(value: int | float) -> bool:
    """Return False for non-finite values and integers too large for float conversion."""
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


def _freeze_json_value(value: Any, *, path: str = "metadata") -> Any:
    """Validate JSON-compatible metadata and recursively make it immutable."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not _is_finite_number(value):
            raise AdapterRequestError(f"{path} must not contain NaN or infinity")
        return value
    if isinstance(value, Mapping):
        frozen: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise AdapterRequestError(f"{path} keys must be strings")
            frozen[key] = _freeze_json_value(item, path=f"{path}.{key}")
        from types import MappingProxyType

        return MappingProxyType(frozen)
    if isinstance(value, (list, tuple)):
        return tuple(
            _freeze_json_value(item, path=f"{path}[{index}]")
            for index, item in enumerate(value)
        )
    raise AdapterRequestError(
        f"{path} must contain only JSON-compatible values"
    )


@dataclass(frozen=True)
class GenerationRequest:
    """One validated generation request independent of the selected runtime."""

    prompt: str
    system_prompt: str | None = None
    temperature: float | None = None
    top_p: float | None = None
    max_new_tokens: int | None = None
    stop: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.prompt, str):
            raise AdapterRequestError("prompt must be a string")
        if not self.prompt.strip():
            raise AdapterRequestError("prompt must not be empty or whitespace-only")
        if len(self.prompt) > MAX_PROMPT_CHARS:
            raise AdapterRequestError(
                f"prompt exceeds maximum length of {MAX_PROMPT_CHARS} characters"
            )
        if self.system_prompt is not None:
            if not isinstance(self.system_prompt, str):
                raise AdapterRequestError("system_prompt must be a string or None")
            if len(self.system_prompt) > MAX_SYSTEM_PROMPT_CHARS:
                raise AdapterRequestError(
                    "system_prompt exceeds maximum length of "
                    f"{MAX_SYSTEM_PROMPT_CHARS} characters"
                )
        if self.temperature is not None:
            if isinstance(self.temperature, bool) or not isinstance(
                self.temperature, (int, float)
            ):
                raise AdapterRequestError("temperature must be a number or None")
            if not _is_finite_number(self.temperature) or not 0 <= self.temperature <= 2:
                raise AdapterRequestError("temperature must be between 0 and 2")
        if self.top_p is not None:
            if isinstance(self.top_p, bool) or not isinstance(self.top_p, (int, float)):
                raise AdapterRequestError("top_p must be a number or None")
            if not _is_finite_number(self.top_p) or not 0 < self.top_p <= 1:
                raise AdapterRequestError("top_p must be greater than 0 and at most 1")
        if self.max_new_tokens is not None:
            if (
                isinstance(self.max_new_tokens, bool)
                or not isinstance(self.max_new_tokens, int)
                or not 1 <= self.max_new_tokens <= self.limits.max_new_tokens
            ):
                raise AdapterRequestError(
                    f"max_new_tokens must be an integer between 1 and {self.limits.max_new_tokens}"
                )
        if not isinstance(self.stop, (tuple, list)):
            raise AdapterRequestError("stop must be a list or tuple of strings")
        if len(self.stop) > self.limits.max_stop_sequences:
            raise AdapterRequestError(
                f"stop must contain at most {self.limits.max_stop_sequences} sequences"
            )
        if any(
            not isinstance(sequence, str)
            or not sequence
            or len(sequence) > self.limits.max_stop_sequence_chars
            for sequence in self.stop
        ):
            raise AdapterRequestError(
                "each stop sequence must be a non-empty string of at most "
                f"{self.limits.max_stop_sequence_chars} characters"
            )
        object.__setattr__(self, "stop", tuple(self.stop))
        if not isinstance(self.metadata, Mapping):
            raise AdapterRequestError("metadata must be a mapping")
        object.__setattr__(self, "metadata", _freeze_json_value(self.metadata))


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


class AdapterRequestError(AdapterError):
    """Raised when a generation request is invalid or exceeds safe bounds."""


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
        self.requests.append(request)
        return GenerationResult(
            text=self._response_text,
            model_id=self._model_id,
            runtime_name=self.runtime_name,
            finish_reason="mock_complete",
            raw_metadata={"mock": True},
        )
