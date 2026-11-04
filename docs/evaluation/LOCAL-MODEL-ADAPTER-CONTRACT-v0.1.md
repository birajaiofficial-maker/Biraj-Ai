# BIRAJ AI — Local Model Adapter Contract v0.1

**Status:** Draft v0.1 — provider-neutral interface and offline test double only.

## Objective

Allow the Evaluation Runner and future BIRAJ AI inference service to work with more than one local inference runtime without coupling business logic to a vendor-specific request or response shape.

## Scope

- Define a normalized request and result contract.
- Define health, model metadata and generation operations.
- Normalize runtime failures into stable adapter exceptions.
- Provide a deterministic mock adapter for offline tests.
- Document requirements for future Ollama and llama.cpp adapters.

## Non-goals

No runtime installation, model download, network request, subprocess launch, server, hardware benchmark, cloud API, or selection of a model/runtime. The mock adapter is not an AI model and its output must never be represented as a real model evaluation.

## Contract

All adapters implement:

- `runtime_name`: stable runtime identifier.
- `health() -> bool`: true only if the runtime is ready for inference.
- `model_info() -> dict`: model identity and runtime metadata.
- `generate(GenerationRequest) -> GenerationResult`: one normalized generation.

GenerationRequest carries prompt, optional system prompt, temperature, top-p, max-new-tokens, stop sequences and non-secret JSON-compatible metadata. The request validates its inputs at construction and recursively freezes metadata so later caller mutation cannot change the request.

GenerationResult carries text, model/runtime identity, optional token counts, TTFT, generation duration, throughput, finish reason and raw non-secret metadata.

Request validation and resource bounds:
- Prompt: must be non-empty and not whitespace-only at request construction; maximum 100,000 characters.
- System prompt: maximum 20,000 characters.
- Temperature: finite number from 0 through 2; extreme integers that cannot be represented as finite floats are rejected.
- Top-p: finite number greater than 0 and at most 1; extreme integers that cannot be represented as finite floats are rejected.
- Max-new-tokens: integer from 1 through 8,192.
- Stop sequences: at most 16 non-empty strings, each at most 256 characters.
- Metadata: recursively immutable, JSON-compatible values only; non-string object keys, non-finite numbers and arbitrary objects are rejected.

Normalized failures:
- `AdapterRequestError` — invalid request or exceeded contract bounds.
- `AdapterUnavailableError`
- `AdapterTimeoutError`
- `AdapterResponseError`

Adapters must not silently retry non-idempotent requests, fabricate missing measurements, log secrets, or return provider-specific response objects to core code.

## Runtime adapter requirements

### Ollama (future)

- Use the local Ollama HTTP interface only when the user has a computer/server ready.
- Verify health and model availability before generation.
- Record exact model tag/digest and Ollama version.
- Normalize stream completion and timing/token fields.
- Explicitly handle model-not-found, timeout, connection and malformed-response errors.

### llama.cpp (future)

- Support a local llama-server endpoint or a separately approved in-process binding; do not assume both.
- Record server/build version, model artifact checksum, quantization and context settings.
- Normalize streaming and non-streaming responses into the same result type.
- Explicitly handle unavailable server, timeout and malformed responses.

These are planned adapters, not implemented integrations.

## Offline test double

`MockAdapter` implements the interface with deterministic output and no external effects. Tests can verify caller behavior, error handling and response normalization without a model. Mock outputs must be labelled `mock/offline` and excluded from model-quality comparisons.

## Security and resource boundaries

- No shell execution or arbitrary command construction in the adapter contract.
- No automatic downloads or external network calls in the offline milestone.
- Do not expose API keys, environment variables or filesystem paths in raw metadata.
- Runtime URLs, when implemented, must default to loopback and reject unexpected remote hosts unless a separate security review approves them.
- Bound request size, generation length, timeouts and concurrent calls in each live adapter.
- Treat model output as untrusted text. Never execute generated code from an adapter.

## Acceptance criteria

- A typed, provider-neutral contract exists.
- Mock adapter supports health, model info and generation.
- Request construction enforces documented parameter ranges, input-size bounds and immutable metadata.
- Mock output and errors are deterministic and tested.
- Core tests can use the mock without installing a runtime.
- Future runtime adapters can implement the protocol without changing request/result consumers.
- Documentation clearly says no real model is executed and no runtime is selected.

## Dependencies

Task 17 — Evaluation Runner v0.1. This contract does not change the offline Runner's manual mode. Integration of a live adapter into the Runner requires a separate implementation task and hardware availability.
