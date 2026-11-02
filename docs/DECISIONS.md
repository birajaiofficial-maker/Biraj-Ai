# BIRAJ AI — Decision Log

This file records confirmed project decisions. Unresolved technical choices stay in the Pending section until evidence supports a decision.

## Confirmed

| ID | Decision | Reason / boundary | Status |
|---|---|---|---|
| D-001 | Use the existing GitHub repository as the central project workspace and source of truth. | Keep code, documentation, history and work tracking together. | Accepted |
| D-002 | Use ChatGPT as the development assistant for planning, coding, debugging, review and GitHub work. | This is a development workflow choice, not a BIRAJ AI runtime dependency. | Accepted |
| D-003 | Do not use OpenAI or Google Gemini as BIRAJ AI runtime model providers. | Runtime model must be evaluated from eligible open-weight/self-hosted options and their actual licenses. | Accepted |
| D-004 | Complete and test the reusable core platform before adding end-user services. | Avoid premature feature expansion and architectural rework. | Accepted |
| D-005 | Defer pricing, subscriptions, business model and promotion planning until after core-platform completion. | Keep current work focused on engineering completion. | Accepted |
| D-006 | Build and verify modules sequentially, with documented interfaces and tests. | Reduce duplicate work, regressions and confusion. | Accepted |

## Pending technical decisions

| Topic | What must be evaluated | Status |
|---|---|---|
| Model family and exact model | Language quality, reasoning/coding, context, license, size, benchmark and resource use | Pending |
| Inference engine | Model compatibility, serving features, throughput, quantization and operational complexity | Pending |
| Hardware / hosting | Local vs cloud, GPU/VRAM, CPU/RAM, availability, cost ceiling and scale | Pending |
| Production database | Data integrity, migrations, backup, operational fit | Pending |
| Memory and retrieval | Data boundaries, retention, retrieval quality, tenant isolation and deletion | Pending |
| Frontend framework | Product requirements, accessibility, maintainability and API integration | Pending |
| Deployment platform | Reliability, security, observability, backups and rollback | Pending |

## Change protocol

For every material architecture or technology choice, record: context, options considered, evidence, decision, consequences, date and status. Update affected architecture/module documents in the same change. Do not silently overwrite a previous accepted decision; add a superseding entry.
