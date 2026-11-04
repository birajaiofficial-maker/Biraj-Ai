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


## 6. Preliminary research update — 2026-11-04 (not a final selection)

### Model shortlist

| Family / exact candidate | License evidence found | Evaluation role | Notes |
|---|---|---|---|
| Qwen3.5-2B / 4B / 9B / 27B | Official Qwen3.5-2B and Qwen3.5-122B-A10B model cards show Apache-2.0. Verify each exact checkpoint before adoption. | Primary family; compare small and medium sizes | Ollama catalogue lists 0.8B, 2B, 4B, 9B, 27B, 35B and larger variants. Reported package sizes are not runtime memory requirements. |
| Gemma 4 E4B / 12B / 26B-A4B | Official Gemma 4 model card shows Apache-2.0. | Secondary family | Model card describes up to 256K context, multilingual support over 140 languages, and multimodal variants. Validate Hindi quality directly. |
| DeepSeek-R1-Distill-Qwen-7B / 14B | R1 repo states R1 MIT, but distilled variants may carry base-model-specific license conditions. Exact checkpoint license must be verified. | Reasoning-focused comparator | Do not use as the default general assistant without tests. |

Official sources:
- Qwen: https://huggingface.co/Qwen/Qwen3.5-2B ; https://huggingface.co/Qwen/Qwen3.5-122B-A10B
- Qwen local catalogue: https://ollama.com/library/qwen3.5
- Gemma 4: https://huggingface.co/google/gemma-4-26B-A4B ; https://deepmind.google/models/gemma/gemma-4/
- DeepSeek R1: https://huggingface.co/deepseek-ai/DeepSeek-R1

### Runtime comparison

| Runtime | Strength | Trade-off | Candidate use |
|---|---|---|---|
| Ollama | Simplest local model pull/run and local HTTP API | Less low-level control; validate exact model/feature support and multi-user production behavior | First developer-machine trial |
| llama.cpp | Quantized GGUF, CPU/GPU hybrid offload, broad hardware backends | More manual setup and tuning; performance depends on backend | Low-cost CPU/GPU flexibility |
| vLLM | GPU serving, batching and OpenAI-compatible API | Linux/GPU-oriented deployment and more operational setup | Later production-serving candidate when GPU/concurrency justify it |

Official references:
- Ollama GPU: https://github.com/ollama/ollama/blob/main/docs/gpu.mdx
- Ollama context and memory: https://github.com/ollama/ollama/blob/main/docs/context-length.mdx
- llama.cpp: https://github.com/ggml-org/llama.cpp
- vLLM GPU installation: https://docs.vllm.ai/en/stable/getting_started/installation/gpu/
- vLLM quantization: https://docs.vllm.ai/en/stable/features/quantization/

### Provisional evaluation plan

- Fixed prompt suite: Hindi (Devanagari), Hinglish (Roman Hindi), English, coding, code explanation, debugging, reasoning, JSON/schema adherence, tool-call formatting, safety/refusal and long-context retrieval.
- Score correctness, instruction following, Hindi/English fluency, code test pass rate, reasoning reliability and structured-output validity.
- Record exact model revision/hash, license, quantization, runtime/version, OS, CPU, GPU/VRAM, system RAM, context size, time-to-first-token, output tokens/sec, peak memory, failure rate and repeatability.
- Test 4K, 8K and 32K context first. Larger context increases memory consumption; do not assume a model's advertised maximum is practical on the target machine.
- Run 30–50 representative prompts per finalist with identical prompts/settings; execute generated code in a sandbox with tests.
- Model-published benchmarks are supporting evidence only, not the selection criterion.

### Memory and hardware caution

Ollama catalogue package download sizes are not minimum VRAM or total RAM requirements. Runtime memory also includes model working memory, KV cache (affected by context length and concurrent sessions), runtime overhead and OS usage. CPU inference is possible with llama.cpp, but throughput must be measured. Do not publish a minimum hardware claim until tested.

### Provisional architecture direction

Keep the BIRAJ AI model adapter provider-neutral. Compare Ollama and llama.cpp locally using the same checkpoint/quantization. Do not hard-code Ollama into application business logic. Keep vLLM as a later serving candidate if a suitable Linux GPU host and concurrency requirement are established. No runtime is selected.

### Pending inputs and approval gates

- Target device CPU, RAM, GPU name, VRAM, OS and free disk space.
- Initial target: developer laptop/local machine or separate always-on server.
- Expected concurrent users and production latency target.
- Exact license review for each selected checkpoint and quantized/converted artifact.
- No model/runtime selection, hardware purchase, cloud GPU or paid service is approved by this research.
