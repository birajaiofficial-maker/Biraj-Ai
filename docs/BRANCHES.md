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

## New workflow

- Work sequentially on `work/open-weight-core`.
- Use `main` as the stable base.
- Open a PR only when a coherent, reviewable milestone is ready.
- Do not create a duplicate branch for work already assigned.
- Keep old PRs/branches intact until useful changes have been identified and the user approves disposition.
- Do not merge, close, delete or force-push as part of routine setup.

## Reconciliation checklist

- [ ] Compare all unique commits in legacy branches with `main` and the new branch.
- [ ] Identify provider-independent changes worth porting (for example, tenant validation fix).
- [ ] Reimplement or selectively port accepted changes with tests.
- [ ] Record final disposition of PR #1 and PR #4.
- [ ] Only then propose closing or deleting historical branches for explicit approval.
