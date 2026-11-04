# BIRAJ AI — Technical Documentation

This folder is the technical source of truth for system architecture, development phases, model/runtime evaluation, module boundaries, testing and engineering workflow.

## Documents

- [Architecture](ARCHITECTURE.md) — runtime boundaries, layers and request flow.
- [Development plan](DEVELOPMENT-PLAN.md) — ordered phases, dependencies and exit gates.
- [Decision log](DECISIONS.md) — accepted decisions and pending choices.
- [Model and runtime evaluation](MODEL-EVALUATION.md) — model/runtime selection criteria; no model is preselected.
- [Local runtime and hardware readiness](LOCAL-RUNTIME-HARDWARE-READINESS.md) — Task 20; Ollama/llama.cpp comparison, host inventory, memory-sizing method, readiness and security gates. No runtime selected.
- [Evaluation prompt suite](evaluation/BIRAJ-PROMPT-SUITE-v0.1.md) — fixed initial Hindi, Hinglish, English, coding, reasoning, JSON, retrieval and safety prompts.
- [Evaluation scoring guide](evaluation/SCORING-GUIDE-v0.1.md) — human scoring rubric, runtime metrics, review gates and scorecard template.
- [Evaluation Runner specification](evaluation/EVALUATION-RUNNER-SPEC-v0.1.md) — offline-first runner scope, data contracts, security boundaries and acceptance criteria.
- [Local Model Adapter contract](evaluation/LOCAL-MODEL-ADAPTER-CONTRACT-v0.1.md) — provider-neutral inference interface and offline mock test double.
- [Evaluation Runner CLI](../tools/evaluation_runner/README.md) — local commands for validation, response/score recording and report generation.
- [Module register](modules/README.md) — one index of modules and their implementation status.
- [Development workflow](DEVELOPMENT-WORKFLOW.md) — task, branch, PR, testing and update rules.
- [Testing strategy](TESTING.md) — test levels and quality gates.
- [Security baseline](SECURITY.md) — authentication, tenant isolation, secrets and threat controls.
- [Branch register](BRANCHES.md) — active and historical branch/PR inventory.

## Record ownership

- GitHub: code, source history, branches, PRs, CI and technical documentation.
- Notion: task tracker, milestones, decisions requiring user approval, progress and change records.
- A Notion Task ID must appear in the corresponding GitHub issue/PR description where practical.
- Do not create duplicate task registers or duplicate module specifications.

## Update rule

A material code or architecture change must update the affected technical document and the matching Notion task/change record in the same work session. Unverified or proposed choices must be labelled as such.
