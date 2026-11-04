# BIRAJ AI — Branch and Pull Request Register

This file records the verified branch/PR state as inspected during migration. Recheck GitHub before every branch operation; this document is not a substitute for live state.

## Branches

| Branch | Purpose | Current disposition |
|---|---|---|
| `main` | Stable integrated baseline | Active; unchanged by this migration branch |
| `work/open-weight-core` | New self-hosted open-weight migration and sequential development | Active; created from `main` for this migration |
| `work/core-platform` | Previous working branch containing Cloudflare-specific PR #4 changes | Legacy/in review; do not merge into new baseline as-is |
| `feature/local-open-model-runtime` | Ollama/Qwen experiment | Historical experiment; evaluate and selectively port only after model/runtime review |
| `docs/project-foundation` | Initial documentation branch | Historical; PR #2 was previously merged per prior branch records |
| `setup/initial-foundation` | Earlier setup branch | Historical; preserve until unique commits are confirmed redundant |

## Open pull requests at migration start

| PR | Branch | Scope | New baseline disposition |
|---|---|---|---|
| [#1](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/1) | `feature/local-open-model-runtime` | Ollama adapter and Qwen2.5 0.5B default experiment | Do not merge automatically. Reuse as evaluation evidence; model/runtime not approved. |
| [#4](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/4) | `work/core-platform` | Tenant validation fix plus Cloudflare Workers AI provider and related policy | Do not merge into new baseline as-is. Review and selectively port provider-independent changes. |

PR #4 is not solely a tenant-name fix; its diff includes Cloudflare Workers AI integration, Cloudflare-only decisions and tests. The PR remains open and unmerged at the time of this record.

Selective reconciliation on `work/open-weight-core` (2026-11-04): tenant-name normalization and bounded per-process Redis-outage fallback were reimplemented with regression tests. Cloudflare provider code and Ollama/Qwen provider defaults were not ported. GitHub Actions run [#33](https://github.com/birajaiofficial-maker/Biraj-Ai/actions/runs/41746723627) passed (7 tests). Compare results: `feature/local-open-model-runtime` is 9 commits ahead / 23 behind the new branch; its unique changes are the five PR #1 files (.env.example, README.md, app/ai.py, app/main.py, tests/test_api.py). `work/core-platform` is 23 commits ahead / 22 behind; its unique changes include the Cloudflare adapter/configuration, provider-specific tests, tenant validation, Redis fallback and API contract/policy documentation. Only the two provider-independent code fixes were ported. PR #1 and PR #4 remain open and unmerged; no historical branches were deleted.

## New workflow

- Work sequentially on `work/open-weight-core`.
- Use `main` as the stable base.
- Open a PR only when a coherent, reviewable milestone is ready.
- Do not create a duplicate branch for work already assigned.
- Keep old PRs/branches intact until useful changes have been identified and the user approves disposition.
- Do not merge, close, delete or force-push as part of routine setup.

## Reconciliation checklist

- [x] Compare unique commits and changed files in both legacy source branches against `work/open-weight-core`.
- [x] Identify provider-independent changes worth porting (tenant validation and Redis outage resilience).
- [x] Reimplement tenant validation and Redis outage fallback with regression tests (execution still pending).
- [x] Record final disposition: both PRs remain open/unmerged and excluded from the new baseline.
- [ ] Only then propose closing or deleting historical branches for explicit approval.
