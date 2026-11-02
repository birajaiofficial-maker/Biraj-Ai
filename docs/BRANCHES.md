# Branch Register and Workflow

This file is the authoritative record of BIRAJ AI branches. Update it whenever a branch is created, repurposed, merged, or deleted. Check GitHub before creating any branch; do not rely on memory alone.

## Current branch register

| Branch | Purpose | Base | Linked PR | Status | Rule |
|---|---|---|---|---|---|
| `main` | Stable, integrated project code and documentation | Repository default | — | Active | Do not work directly here; merge reviewed changes into it. |
| `docs/project-foundation` | Initial project structure and technical documentation | `main` | [#2](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/2) | Active; PR is draft and CI passes | Finish review and merge this documentation change before starting core implementation. |
| `feature/local-open-model-runtime` | Experimental Ollama/Qwen local-runtime proposal | `main` | [#1](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/1) | Active; PR is draft and CI passes; architecture/model approval pending | Do not merge or use as the selected runtime until model, license, hardware and runtime evaluation is approved. |
| `setup/initial-foundation` | Earlier initial-foundation setup branch | Unknown from current branch metadata | — | Exists; purpose and disposition need review | Do not reuse or delete until its commits are compared with `main` and the active PRs. |

## Branch policy

1. **Check first:** Before creating a branch, inspect the current branch list, open pull requests, and the branch register.
2. **No duplicate branches:** Never create another branch for work already assigned to an active branch.
3. **Keep the branch count small:** Prefer `main` plus one active working branch for sequential core-platform development. Create a separate branch only when work must be isolated or developed in parallel.
4. **Naming:** Use short purpose-based names, such as `work/core-platform` or `fix/tenant-auth`. Do not create numbered or date-stamped branches without a concrete need.
5. **One task, one PR:** A branch should have one clear objective and one pull request. Do not mix unrelated changes.
6. **No direct main edits:** All implementation and documentation changes go through a pull request into `main`.
7. **After merge:** Record the merge date and PR in the history below. Delete short-lived branches only after confirming the merge. Keep only an intentionally designated long-lived working branch.
8. **Before every new task:** State the repository, branch, task, and PR (if one exists) in the work record. If the correct branch is unclear, stop and resolve it before writing code.

## Current workflow

- Complete review of PR #2 on `docs/project-foundation`.
- PR #1 is a separate experimental runtime proposal. Its passing tests do not approve Qwen as the final model or Ollama as the final inference engine.
- After PR #2 is merged, use one continuing branch named `work/core-platform` for sequential core-platform work and open a fresh PR for each coherent milestone. Do not create another branch for each small module.
- Before creating `work/core-platform`, inspect and reconcile the existing `feature/local-open-model-runtime` and `setup/initial-foundation` branches. Do not create a duplicate working branch.
- Only introduce a separate fix/feature branch if a change genuinely needs isolation or parallel work.

## Change history

| Date (UTC) | Branch | Change | PR / Result |
|---|---|---|---|
| 2026-11-02 | `docs/project-foundation` | Created initial project documentation and structure; branch inventory corrected to include all existing branches | [PR #2](https://github.com/birajaiofficial-maker/Biraj-Ai/pull/2), open draft; not merged |

## Required update checklist

When branch state changes, update this file with:
- exact branch name;
- purpose and base branch;
- linked pull request;
- current status (active, merged, or deleted);
- merge date/result, if applicable.
