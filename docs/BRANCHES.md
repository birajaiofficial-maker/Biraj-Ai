# Branch Register and Workflow

This file is the authoritative record of BIRAJ AI branches. Update it whenever a branch is created, repurposed, merged, or deleted. Check GitHub before creating any branch; do not rely on memory alone.

## Current branch register

| Branch | Purpose | Base | Linked PR | Status | Rule |
|---|---|---|---|---|---|
| `main` | Stable, integrated project code and documentation | Repository default | — | Active | Do not work directly here; merge reviewed changes into it. |
| `work/core-platform` | Single continuing branch for sequential core-platform implementation | `main` | None yet | Active | Use for the next coherent milestone; open a PR when the milestone is reviewable. |
| `feature/local-open-model-runtime` | Experimental Ollama/Qwen local-runtime proposal | `main` (diverged; 9 commits ahead, 1 behind at last comparison) | [#1](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/1) | Open draft; CI passed on its current reviewed commit; architecture/model approval pending | Keep isolated. Do not merge or adopt its default model/runtime without explicit technical evaluation. |
| `docs/project-foundation` | Initial project structure and technical documentation | `main` | [#2](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/2) | Merged 2026-11-02; short-lived branch cleanup pending | Do not continue work here. Delete after confirming the merge. |
| `setup/initial-foundation` | Earlier initial-foundation setup branch | Historical ancestor of `main` | — | No unique commits ahead of `main`; 33 commits behind at last comparison; cleanup pending | Do not reuse. Delete after confirming it is no longer needed. |

## Branch policy

1. **Check first:** Before creating a branch, inspect the current branch list, open pull requests, and this register.
2. **No duplicate branches:** Never create another branch for work already assigned to an active branch.
3. **Keep the branch count small:** Prefer `main` plus one active working branch for sequential core-platform development. Create a separate branch only when work must be isolated or developed in parallel.
4. **Naming:** Use short purpose-based names, such as `work/core-platform` or `fix/tenant-auth`. Do not create numbered or date-stamped branches without a concrete need.
5. **One task, one PR:** The continuing work branch may carry sequential milestones; open a fresh PR for each coherent milestone. Do not create another branch for each small module.
6. **No direct main edits:** All implementation and documentation changes go through a pull request into `main`.
7. **After merge:** Record the merge date and PR in the history below. Delete short-lived branches only after confirming the merge. Keep only the intentionally designated continuing working branch.
8. **Before every new task:** State the repository, branch, task, and PR (if one exists) in the work record. If the correct branch is unclear, stop and resolve it before writing code.

## Current workflow

- Continue sequential core-platform work on `work/core-platform`.
- PR #1 remains an experimental local-runtime proposal. Its passing tests do not approve Qwen as the final model or Ollama as the final inference engine.
- First implementation milestone: Phase 0 hardening, beginning with tenant-name normalization and regression tests; decide Redis outage behavior before changing it.
- Do not create another working branch unless a task genuinely requires isolation or parallel work.

## Change history

| Date (UTC) | Branch | Change | PR / Result |
|---|---|---|---|
| 2026-11-02 | `docs/project-foundation` | Created initial project documentation and structure | [PR #2](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/2), merged into `main` as `6cee4d7cc60fc9df4c0603783407fc50d6708f34` |
| 2026-11-02 | `work/core-platform` | Created the single continuing implementation branch from merged `main` | Active; no PR yet |

## Required update checklist

When branch state changes, update this file with:
- exact branch name;
- purpose and base branch;
- linked pull request;
- current status (active, merged, or deleted);
- merge date/result, if applicable.
