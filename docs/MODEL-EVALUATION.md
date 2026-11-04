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


## 7. Hindi and Indic-language evaluation research — 2026-11-04

### Benchmark sources to adapt

- **IndicGenBench (ACL 2024):** evaluates user-facing generation across 29 Indic languages and 13 scripts, including cross-lingual summarization, translation and question answering. Use it as a reference for language coverage and task design; verify dataset terms and exact Hindi subset availability before incorporating any data.
  - Paper: https://aclanthology.org/2024.acl-long.595/
- **Hindi LLM evaluation suite (2025 preprint):** proposes IFEval-Hi, MT-Bench-Hi, GSM8K-Hi, ChatRAG-Hi and BFCL-Hi, addressing instruction following, chat, math reasoning, RAG and function calling in Hindi. Treat this as a candidate evaluation reference, not as a verified scorecard for our shortlisted models. Check dataset access, licensing and reproducibility before reuse.
  - Paper: https://arxiv.org/abs/2508.19831
- **EleutherAI LM Evaluation Harness:** provides a reproducible framework for running standard language-model tasks and custom evaluations across supported model backends. It can supplement, but cannot replace, BIRAJ-specific Hindi/Hinglish tests.
  - Documentation: https://lm-evaluation-harness.readthedocs.io/

### BIRAJ-specific test-set design

Create a small, versioned, manually reviewed internal test set with separate slices:
1. Hindi in Devanagari: natural conversation, explanations, summaries and multi-step instructions.
2. Hinglish in Roman script: spelling variation, code-switching and colloquial phrasing.
3. English: general assistant quality and technical explanations.
4. Coding: generate a small function, explain unfamiliar code, diagnose a bug and write tests; grade by executing tests in an isolated sandbox.
5. Structured output: exact JSON schema, missing fields, invalid input and tool-call argument formatting.
6. Reasoning and factuality: multi-step questions with a known answer key; penalize unsupported claims and fabricated citations.
7. Retrieval/context: place known facts in a long supplied document and test exact recall, conflicting statements and abstention.
8. Safety: benign requests, disallowed requests and ambiguous requests; assess both unsafe compliance and excessive refusal.

For each prompt, store the expected answer or rubric, language/script label, difficulty, source/author, dataset license (if external), and test-set version. Keep a held-out set that is not used to tune prompts. Have a Hindi-fluent reviewer score language naturalness and meaning preservation; automatic translation metrics alone are insufficient.

### Scoring and decision discipline

- Report per-slice scores, not only one aggregate score. A strong English result must not hide weak Hindi/Hinglish performance.
- Suggested initial weighting for an internal comparison: Hindi + Hinglish 35%, coding 25%, reasoning/factuality 15%, instruction/JSON/tool formatting 15%, safety/reliability 10%. Treat these weights as a proposal to review, not an approved product requirement.
- Publish both quality and operating cost: success rate, code test pass rate, JSON validity, refusal precision, time-to-first-token, tokens/sec, peak RAM/VRAM and failure rate.
- Run the same test suite against each candidate with pinned model revisions, runtime versions, quantization and decoding parameters. Save raw outputs so scores can be audited.
- Do not copy benchmark scores from model vendors into the BIRAJ scorecard as if they were independently reproduced.

### License clarification from official sources

- A surfaced official Qwen3.5-9B Hugging Face model card identifies that exact checkpoint as Apache-2.0. This supports adding Qwen3.5-9B as a candidate, but does not replace checking the exact revision and any separately licensed tokenizer or converted artifact: https://huggingface.co/Qwen/Qwen3.5-9B
- Google's official Gemma 4 model card and launch material identify Apache-2.0: https://ai.google.dev/gemma/docs/core/model_card_4 and https://blog.google/innovation-and-ai/technology/developers-tools/gemma-4/
- DeepSeek's official R1 repository describes the R1 series as MIT but explicitly distinguishes the upstream licenses for distilled checkpoints: Qwen-derived variants trace to Qwen 2.5 Apache-2.0; Llama-derived variants trace to Llama 3.1/3.3 licenses. For any exact distilled checkpoint, retain the model card, upstream license and revision as part of the approval record: https://github.com/deepseek-ai/DeepSeek-R1

### Current conclusion after this research

Hindi evaluation needs a dedicated test slice and human review; broad multilingual support claims are not evidence of usable Hindi/Hinglish quality. IndicGenBench and the 2025 Hindi benchmark paper provide useful task references, while BIRAJ must maintain its own versioned prompts and reproducible raw results. No model or runtime is selected. Hardware and local benchmark execution remain outstanding.
