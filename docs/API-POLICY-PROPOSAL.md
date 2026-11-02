# API Contract Policy Proposal (Draft)

**Status:** Proposal only — not approved for runtime implementation  
**Scope:** External BIRAJ AI client applications  
**Current compatibility baseline:** `/api/v1` and the endpoints documented in [API-CONTRACT.md](API-CONTRACT.md)

This document proposes stable API rules. It does not change runtime behavior and must not be treated as a finalized public contract until the owner approves it.

## 1. Versioning

- Keep the existing `/api/v1` prefix.
- Additive, backward-compatible fields and endpoints may be introduced within v1.
- Do not rename or remove existing fields, change their meaning, or change required inputs within v1.
- Any breaking change requires a new major path such as `/api/v2`.
- Keep old versions available during a documented migration window; define the duration before announcing a deprecation.
- Include the API version in documentation and automated contract tests.

## 2. Standard error envelope

Proposed shape:

```json
{
  "error": {
    "code": "STABLE_MACHINE_CODE",
    "message": "A safe, user-readable explanation.",
    "request_id": "request-correlation-id"
  }
}
```

- `code` is stable and intended for client logic; clients must not parse the human-readable message.
- `message` must not expose secrets, stack traces, internal hostnames, raw provider responses, or credential details.
- Preserve appropriate HTTP status semantics.
- Document the supported error codes and status mapping.
- Avoid returning different error shapes from different routers.

## 3. Request correlation

- Generate a request ID at the API boundary for every request.
- Return it in the `X-Request-ID` response header and include it in the error envelope.
- If accepting a caller-supplied correlation ID is later approved, validate and bound its length/character set; do not blindly trust arbitrary header values.
- Include the request ID in structured logs while redacting API keys, provider tokens, prompts, and sensitive user data.
- Request IDs are for tracing, not authentication or authorization.

## 4. Streaming

- Defer streaming until the non-streaming contract is stable and a real client requirement is identified.
- If approved later, evaluate Server-Sent Events (SSE) first for text generation.
- Specify event names, chunk format, terminal event, error behavior after headers are sent, client disconnect handling, timeouts, and usage accounting before implementation.
- Keep the existing non-streaming endpoint available for compatibility.

## 5. Usage limits and provider quota

Keep two independent controls:

1. **BIRAJ tenant quota:** platform-defined limits assigned to a tenant/application.
2. **Cloudflare provider quota:** the actual account/model limits and provider-side throttling or availability.

Proposed behavior:

- Never silently enable paid usage, billing, or a paid plan.
- When a BIRAJ tenant quota is exhausted, reject predictably with a documented quota error and retry guidance only where meaningful.
- When Cloudflare throttles or quota is exhausted, map it to a distinct upstream/provider error; do not misreport it as the tenant's quota.
- Do not invent fixed free-tier limits in code or documentation. Configure limits only after the account's current limits and intended policy are verified.
- Record usage safely and avoid charging/counting failed requests as successful generation; define exact metering semantics before implementation.
- Fail safely when quota state cannot be trusted, but do not turn unrelated transient infrastructure faults into unnecessary permanent access denial.

## 6. Compatibility and rollout

- Add contract tests for success and error payloads before changing runtime routes.
- Keep current clients working while additive changes are introduced.
- Document any behavior change, migration steps, and rollback path.
- Do not implement this proposal until it is approved and recorded in the Decision Register.

## 7. Decisions required from owner

- Approve or revise the v1/v2 compatibility rule.
- Approve the error envelope fields and HTTP status mapping.
- Approve request ID generation and response header behavior.
- Decide whether/when streaming is required.
- Approve the distinction and policy for tenant quota versus provider quota.
- Approve metering semantics and configurable quota ownership.

Until these decisions are confirmed, this file is a design proposal only.
