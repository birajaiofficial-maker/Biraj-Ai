# Open-Weight Model and Inference Runtime Evaluation

**Status:** Evaluation framework only. No model or runtime is selected.

## 1. Selection rules

- Confirm the exact model license and commercial-use/redistribution restrictions.
- Prefer weights that can be downloaded and served locally or on BIRAJ-controlled hardware.
- Do not assume model weights, tokenizer, runtime and quantization artifacts share one license.
- Benchmark actual candidate builds; do not choose by model name or leaderboard alone.
- Do not provision paid infrastructure during evaluation without explicit approval.

## 2. Model criteria

| Criterion | Evidence required |
|---|---|
| License | Exact license text, restrictions, attribution and commercial-use terms |
| Hindi quality | Real Hindi prompts and evaluation rubric |
| English quality | Instruction following and answer quality |
| Reasoning/coding | Representative tasks and reproducible scoring |
| Context | Supported context window and measured behavior |
| Hardware | RAM/VRAM at target quantization and context |
| Performance | Time-to-first-token, tokens/sec and concurrency |
| Reliability | Hallucination behavior, refusal quality and stability |
| Maintenance | Release cadence, model provenance and security posture |

## 3. Runtime candidates to evaluate

- **Ollama:** simple local development and model management; assess operational suitability beyond a single-user laptop.
- **vLLM:** high-throughput serving candidate; assess GPU/platform compatibility and deployment complexity.
- **llama.cpp:** CPU/GPU and quantized GGUF serving candidate; assess performance and integration requirements.

These are candidates, not endorsements or final decisions. Add alternatives only when there is a clear technical reason.

## 4. Evaluation protocol

1. Record target device specifications and available memory.
2. Select a small, medium and larger candidate only if hardware can test them.
3. Verify exact licenses and artifact provenance.
4. Use the same Hindi/English prompt set, context length and decoding settings.
5. Record latency, throughput, memory, failure rate and answer quality.
6. Compare local CPU/GPU feasibility and operational complexity.
7. Produce a recommendation with trade-offs and unresolved risks.
8. Request explicit acceptance before updating the accepted model/runtime decision.

## 5. Required result table

| Candidate | License reviewed | Hindi/English score | VRAM/RAM | Latency | Runtime | Decision |
|---|---|---|---|---|---|---|
| Not yet benchmarked | — | — | — | — | — | Pending |

No model is considered selected until this table is supported by reproducible evidence and a recorded approval.
