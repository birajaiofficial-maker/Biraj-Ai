# BIRAJ AI — Evaluation Runner Specification

**Status:** Draft v0.1 — implementation contract; not a model-selection decision.

## 1. Purpose

Provide a small, local-first and provider-neutral tool to execute the versioned BIRAJ prompt suite when a supported model host becomes available, preserve raw model responses, capture human scores, and produce auditable comparisons.

The first milestone must also be useful before a model host exists: validate the prompt suite, create run records, accept manually supplied responses and scores, and generate reports from recorded data.

## 2. Scope for v0.1

### In scope

- Python command-line interface; Python standard library only for the initial runner.
- Validate the prompt-suite file and required fields before a run.
- Create a unique run folder with immutable run metadata.
- Store one response record per prompt/model attempt as JSON Lines (JSONL).
- Store human scorecards separately from raw responses.
- Keep quality scores separate from measured runtime metrics.
- Calculate category means and provisional weighted score using the v0.1 Scoring Guide.
- Mark the overall score incomplete when a required category has no valid observations.
- Generate a machine-readable JSON report and a readable Markdown report.
- Support a manual/offline mode so development does not require a model, API key, server, GPU or paid service.
- Preserve failed, skipped and incomplete attempts; never silently discard them.

### Out of scope

- Hosting or downloading model weights.
- Selecting Qwen, Gemma, DeepSeek or any other model.
- Calling OpenAI, Gemini, Cloudflare Workers AI or another hosted model API.
- Provisioning cloud/GPU infrastructure.
- Automatically deciding subjective Hindi/Hinglish quality or safety scores.
- Executing generated code on the runner host or production systems.
- Model fine-tuning, prompt optimization or benchmark leaderboard claims.

## 3. Proposed repository layout

```text
tools/evaluation_runner/
  README.md
  runner.py
  schemas/
    prompt.schema.json
    response.schema.json
    scorecard.schema.json
  examples/
    sample-prompts.jsonl
    sample-scorecard.json
  results/                 # generated locally; never commit raw outputs
    <run_id>/
      run.json
      responses.jsonl
      scorecards.jsonl
      report.json
      report.md
```

The prompt suite remains the source of test prompts in `docs/evaluation/BIRAJ-PROMPT-SUITE-v0.1.md`. Do not copy and maintain a second canonical prompt list. A machine-readable export may be generated from that document or maintained as a versioned companion only if each prompt has a stable ID and the two representations are checked for drift.

## 4. Run lifecycle

1. Validate the suite and its version.
2. Create a run with a unique ID and record model/runtime/hardware metadata.
3. Execute prompts through an adapter when a local runtime is available, or import/record responses manually in offline mode.
4. Persist raw response text and per-prompt execution metadata.
5. Add a human-reviewed scorecard for each applicable prompt.
6. Validate score ranges, required fields and category applicability.
7. Generate reports; show missing categories and missing runtime measurements explicitly.
8. Preserve the run unchanged. Corrections create a new scorecard revision or a new run; raw output is not overwritten silently.

## 5. Provider-neutral adapter contract (future live execution)

The runner may later support local adapters, but the core must not depend on a specific inference engine.

Conceptual adapter operations:

- `generate(prompt, settings) -> response`
- `health() -> runtime_status`
- `model_info() -> model_metadata`

Initial future adapters may target Ollama and llama.cpp only after separate compatibility checks. vLLM remains a later serving candidate. No adapter is required to complete the offline v0.1 milestone.

Every live request must record timeout, error state, prompt/output token counts when available, TTFT, generation duration and tokens/second. Missing measurements must be `null`/N/A, never fabricated.

## 6. Data contracts

### Run metadata

Required: `run_id`, creation timestamp (UTC), prompt-suite ID/version and checksum, model ID, exact model revision (or explicitly unknown), license-review state, quantization, runtime and version (or manual/offline), decoding settings, context limit, operating system, CPU, system RAM, GPU and VRAM.

### Response record

Required: run ID, prompt ID, attempt number, status, raw response or explicit missing-response reason, start/end timestamps, and raw-output reference. Runtime measurements are optional nullable numeric fields. Do not store secrets, API keys or personal data in prompts/results.

### Scorecard

Required: run ID, prompt ID, reviewer identifier/label, review timestamp, and applicable 0–4 values for correctness, instruction adherence, language quality, reasoning/factuality, safety and structured-output validity. N/A must remain distinct from zero. Include concise evidence/notes for low scores and safety failures.

## 7. Scoring and reporting rules

- Read weights and score semantics from the versioned Scoring Guide; do not hard-code a second conflicting policy.
- Report each category mean and sample count.
- Provisional weights for v0.1: Hindi + Hinglish 35%, Coding 25%, Reasoning + factuality 15%, Instructions + JSON 15%, Safety + reliability 10%.
- Overall quality score stays on a 0–4 scale; percentage is display-only.
- If any required category has no valid observations, overall score is `incomplete`, not zero and not a partial weighted score.
- Runtime performance is a separate report section and must never be folded into the human quality score.
- Hard review gates (license, harmful compliance, secret exposure, reproducibility and hardware feasibility) remain visible and cannot be averaged away.
- Each hard review gate is recorded as pending/pass/blocked in JSON and Markdown reports.
- Missing context-size, system-RAM and GPU-VRAM measurements are recorded explicitly as unknown.
- Compare candidates only when prompt suite, model revision, quantization, runtime settings and context budget are sufficiently aligned. Record differences.

## 8. Privacy, safety and resource controls

- Local filesystem only in v0.1; no outbound network calls.
- No secrets in source files, test fixtures, logs or results.
- Generated code is stored as text only. Any later execution must use a separately designed isolated sandbox with resource and network restrictions.
- Results directory is local and git-ignored; raw model outputs are not committed by default.
- Set input-size limits and validate JSONL records to avoid accidental memory exhaustion or malformed data.
- Do not automatically delete or overwrite run evidence.

## 9. Test plan

- Valid and invalid prompt-suite records.
- Missing/duplicate prompt IDs.
- Invalid score values, N/A handling and missing category behavior.
- Correct weighted-score calculation and 0–4 bounds.
- Runtime metrics kept separate from quality scores.
- Failed/skipped attempts retained in reports.
- Safe path handling and refusal to overwrite an existing run.
- Deterministic report generation from the same input records.
- No network access or model execution in offline tests.

## 10. Acceptance criteria

- A user can validate the prompt suite without a model or server.
- A user can create an offline run and record a response and scorecard.
- Every run captures the required metadata or explicitly marks unknown values.
- Raw responses and human scorecards are stored separately and linked by run/prompt IDs.
- Report output includes per-category scores, sample counts, weighted score or incomplete status, hard-gate flags and separate runtime metrics.
- Invalid input is rejected with an actionable message; existing run evidence is not overwritten.
- Unit tests cover scoring, validation, persistence and report generation.
- Documentation explains exact commands and the limits of offline mode.
- No model/runtime selection, paid service or infrastructure provisioning occurs as part of this task.

## 11. Dependencies and open decisions

- Depends on Task 10's prompt suite and scoring guide.
- Prompt-suite machine-readable representation: generated export vs checked-in companion file; decide during implementation.
- Live adapter protocol and timeout/retry policy require a separate design before live model execution.
- Final result retention, backup and reviewer identity policy remain open.

**Current state:** Specification only. No model has been executed by this runner. No model/runtime is selected and no paid infrastructure is approved.
