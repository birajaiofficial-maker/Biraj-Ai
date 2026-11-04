# BIRAJ AI Evaluation Runner v0.1

Offline-first CLI for validating the fixed prompt suite, recording model responses and human scorecards, and generating auditable reports. Uses only the Python standard library.

## Requirements

- Python 3.11+
- Run commands from the repository root.
- No model server, GPU, API key, network access or paid service is required for offline mode.

## 1. Validate the prompt suite

```bash
python -m tools.evaluation_runner.runner validate-suite
```

The runner reads stable prompt IDs and prompt text from `docs/evaluation/BIRAJ-PROMPT-SUITE-v0.1.md`; it does not maintain a second hand-edited prompt list.

## 2. Create an offline run

```bash
python -m tools.evaluation_runner.runner new-run --model-id "candidate-not-selected"
```

Optional metadata can be supplied with `--model-revision`, `--license-review`, `--quantization`, `--runtime`, `--runtime-version`, `--context-tokens`, `--cpu`, `--system-ram-mb`, `--gpu`, `--gpu-vram-mb` and `--decoding-settings-json`.

The command creates a unique directory under `tools/evaluation_runner/results/`. It refuses to reuse an existing run directory. Unknown values are recorded explicitly.

## 3. Record a response

Use the run directory printed by `new-run`. For a short response:

```bash
python -m tools.evaluation_runner.runner record-response \
  --run-dir "tools/evaluation_runner/results/REPLACE_WITH_RUN_ID" \
  --prompt-id HI-01 \
  --response "यहाँ मॉडल का मूल जवाब रखें"
```

For long responses, prefer `--response-file path/to/response.txt`. Failed and skipped attempts can be recorded with `--status failed` or `--status skipped` and `--failure-note`. Runtime measurements are optional; omitted values remain null.

## 4. Record a human scorecard

Create a local JSON file (do not commit it) with this shape:

```json
{
  "reviewer": "reviewer-1",
  "correctness_0_4": 4,
  "instruction_0_4": 3,
  "language_0_4": 4,
  "reasoning_0_4": null,
  "safety_0_4": null,
  "format_0_4": null,
  "notes": "Meaning is preserved; minor formatting issue.",
  "evidence": "The answer follows the requested two-point structure."
}
```

Use JSON null for N/A, not zero. At least one dimension must have a numeric score. A completed response for the same prompt and attempt must exist before a scorecard can be recorded.

## 5. Generate reports

```bash
python -m tools.evaluation_runner.runner report \
  --run-dir "tools/evaluation_runner/results/REPLACE_WITH_RUN_ID"
```

The runner writes `report.json` and `report.md`. Quality is marked **incomplete** until every required weighted category has valid score observations. English prompts are shown as an auxiliary slice and do not silently change the provisional weights. Runtime medians are reported separately from human quality scores.

## 6. Adapter contract (offline only)

The provider-neutral interface and deterministic mock are in `adapters.py`. Request construction validates generation parameters and bounded input sizes, and recursively freezes JSON-compatible metadata. They allow tests to verify request/result handling without Ollama, llama.cpp or any actual model.

See [Local Model Adapter Contract v0.1](../../../docs/evaluation/LOCAL-MODEL-ADAPTER-CONTRACT-v0.1.md). The mock is not a real model and must not be counted as an evaluation result.

## Data and safety rules

- `responses.jsonl` stores raw response text and attempt metadata.
- `scorecards.jsonl` stores reviewer scores separately.
- `run.json` pins suite checksum, scoring weights, model/runtime metadata and hardware fields.
- Results may contain sensitive test content. Keep them local and do not commit them.
- Generated code is stored as text only; this runner never executes model-generated code.
- Offline mode does not call any model or external API. It does not prove that a model can run or that reported metadata is true.

See [the runner specification](../../../docs/evaluation/EVALUATION-RUNNER-SPEC-v0.1.md) and [scoring guide](../../../docs/evaluation/SCORING-GUIDE-v0.1.md).
