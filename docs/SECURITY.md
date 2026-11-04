# BIRAJ AI — Security Baseline

**Status:** Required controls baseline; detailed threat model and implementation verification remain pending.

## Identity and access

- Authenticate every protected API operation.
- Hash API keys at rest; display raw keys only once at creation.
- Apply tenant scoping to every tenant-owned query and write.
- Enforce authorization at the service boundary, not only in the UI.
- Test cross-tenant access attempts and key revocation.

## Secrets and configuration

- Keep secrets in environment/secret storage, never in source control, logs, screenshots or Notion.
- Validate required configuration at startup.
- Use separate development and production credentials.
- Do not expose internal inference URLs, filesystem paths or credentials in public API responses.

## Self-hosted inference security

- Keep inference service on localhost/private network; do not expose model ports publicly by default.
- Restrict model artifact sources and verify checksums/signatures where available.
- Review model and runtime licenses and supply-chain risks.
- Set request size, context, output-token, timeout and concurrency limits.
- Do not allow model output to bypass application authorization.
- No hosted-provider fallback.

## Data and memory

- Define tenant ownership, retention and deletion before persistent memory is enabled.
- Prevent cross-tenant retrieval.
- Avoid storing sensitive content unless required and approved.
- Log metadata needed for security without unnecessarily logging prompts, responses or secrets.

## Resilience

- Distinguish liveness from readiness.
- Use bounded timeouts and resource limits.
- Document Redis/inference/database outage behavior.
- When Redis is configured but unavailable, the API uses a bounded per-process emergency rate limiter rather than denying every authenticated request. This fallback is process-local, not globally shared across multiple app instances. Responses expose `X-RateLimit-Scope: process` so clients/operators can distinguish it from the Redis-backed shared limit. It is best-effort emergency protection only; do not treat it as a distributed quota or production abuse-control boundary. Monitor and restore Redis. Production multi-instance deployments must use a healthy shared limiter or an explicitly approved distributed alternative.

## Release gates

- Threat model reviewed.
- Auth, tenant isolation and API-key tests pass.
- Dependency and model artifact provenance reviewed.
- Secret scanning and dependency checks pass.
- Backup/restore and rollback procedures verified before production deployment.
