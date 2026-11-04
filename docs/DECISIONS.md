# BIRAJ AI — Decision Log

This is the authoritative record of project decisions. Accepted decisions are not silently overwritten; changes require a superseding entry. Proposed technical options remain pending until evidence and approval exist.

## Accepted decisions

| ID | Decision | Boundary | Status |
|---|---|---|---|
| D-001 | Use the existing GitHub repository as the central engineering workspace. | Preserve code, history, PRs and CI. | Accepted |
| D-002 | Use ChatGPT as a development assistant. | Planning/coding/review only; not a BIRAJ AI runtime dependency. | Accepted |
| D-003 | Do not use OpenAI or Google Gemini as BIRAJ AI runtime model providers. | No API dependency on either provider. | Accepted |
| D-004 | Build BIRAJ AI around an eligible open-weight model served on BIRAJ-controlled infrastructure. | Exact model/runtime pending; self-hosted is the target boundary. | Accepted |
| D-005 | Do not use Cloudflare Workers AI or another hosted model API as the production inference dependency. | No silent hosted-provider fallback. | Accepted |
| D-006 | Complete and test the reusable core platform before expanding end-user services. | Prevent premature feature expansion. | Accepted |
| D-007 | Develop modules sequentially with one authoritative task record and explicit acceptance criteria. | Avoid duplicate work and undocumented changes. | Accepted |
| D-008 | Prefer local/free development and require explicit approval for paid services or infrastructure. | No paid GPU, cloud, subscription or vendor commitment without approval. | Accepted |
| D-009 | Preserve historical branches and PRs until their unique work has been reviewed. | No blind deletion or merging. | Accepted |

## Superseded / historical decisions

| ID | Previous direction | Current disposition |
|---|---|---|
| H-001 | Cloudflare Workers AI only, recorded on the old `work/core-platform` branch and in PR #4 | Superseded by D-004/D-005 for the new baseline; PR #4 remains unmerged and excluded. |
| H-002 | Ollama with Qwen2.5 0.5B as a default in PR #1 | Experiment only; not a final model/runtime selection. Evaluate license, quality and hardware before adoption. |

## Pending technical decisions

Exact model/license, inference runtime, hardware, database, memory/retrieval, frontend and deployment target remain pending.

## Decision change protocol

Record context, options, evidence, decision, consequences, date, owner and status. Update architecture, module register and Notion decision record in the same change. Never convert an experimental branch or passing unit test into an accepted architecture decision.
