# BIRAJ AI — Decision Log

This file records confirmed project decisions. Unresolved technical choices stay in the Pending section until evidence supports a decision.

## Confirmed

| ID | Decision | Reason / boundary | Status |
|---|---|---|---|
| D-001 | Use the existing GitHub repository as the central project workspace and source of truth. | Keep code, documentation, history and CI together. | Accepted |
| D-002 | Use ChatGPT as the development assistant for planning, coding, debugging, review and GitHub work. | This is a development workflow choice, not a BIRAJ AI runtime dependency. | Accepted |
| D-003 | Do not use OpenAI or Google Gemini as BIRAJ AI runtime model providers. | Explicit runtime-provider boundary. | Accepted |
| D-004 | Complete and test the reusable core platform before adding end-user services. | Avoid premature feature expansion and architectural rework. | Accepted |
| D-005 | Defer pricing, subscriptions, business model and promotion planning until after core-platform completion. | Keep current work focused on engineering completion. | Accepted |
| D-006 | Build and verify modules sequentially, with documented interfaces and tests. | Reduce duplicate work, regressions and confusion. | Accepted |
| D-007 | Cloudflare Workers AI is the only approved runtime AI provider at this stage. | No OpenAI, Gemini, Groq, Ollama or other runtime provider; no automatic provider fallback. | Accepted |
| D-008 | Keep inference disabled until Cloudflare account configuration, model access, quota and billing safeguards are verified. | Prevent unintended paid usage; no paid plan or billing change without explicit approval. | Accepted |
| D-009 | Keep the existing two-branch development workflow: main for stable and work/core-platform for ongoing work. | No new task branches, automatic PRs or merges; merge only after explicit user instruction. | Accepted |

## Pending technical decisions

| Topic | What must be evaluated | Status |
|---|---|---|
| Cloudflare account readiness | Token scope, model availability, free quota, quota exhaustion behavior and billing guardrails | Pending verification |
| Production database | Data integrity, migrations, backup, operational fit | Pending |
| Memory and retrieval | Data boundaries, retention, retrieval quality, tenant isolation and deletion | Pending |
| Frontend framework | Product requirements, accessibility, maintainability and API integration | Separate client apps; framework pending |
| Deployment platform | Reliability, security, observability, backups and rollback | Pending |

## Change protocol

For every material architecture or technology choice, record: context, options considered, evidence, decision, consequences, date and status. Update affected architecture/module documents in the same change. Do not silently overwrite a previous accepted decision; add a superseding entry.
