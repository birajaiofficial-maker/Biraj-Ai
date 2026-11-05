# Local Model Runtime & Hardware Readiness — Task 20

**Task:** 20 — Local Model Runtime Research & Hardware Readiness  
**Status:** Research in progress; no runtime selected  
**Branch:** `work/open-weight-core`  
**Parent workstream:** Task 10 — Evaluate open-weight model candidates and self-hosted inference runtime  
**Evidence date:** 2026-11-04

## 1. Purpose and boundary

This document defines the hardware inventory, runtime comparison criteria and readiness gates required before BIRAJ AI attempts local model execution.

It is a focused readiness workstream under Task 10. It does not replace Task 10's final model/runtime evaluation or approval.

**Current result:** the eventual model-host hardware profile is unknown. The user's Android phone is the development/control device; it is not evidence that the phone is the intended inference host or that it can host a selected model.

No runtime or model is selected. No software installation, model download, live inference, benchmark, paid infrastructure or hardware purchase is authorized by this research.

## 2. Runtime comparison — evidence-backed, not a selection

| Dimension | Ollama | llama.cpp |
|---|---|---|
| Primary role | Convenient local model runner and model lifecycle/API layer | Low-level inference engine and server for GGUF model files |
| Model format / distribution | Provides a model library and managed local model storage; exact model packaging varies | Primarily GGUF; supports multiple quantization levels |
| CPU inference | Supported; actual speed depends on CPU, memory bandwidth, model and context | CPU-oriented path is a core use case; actual speed depends on CPU instruction support, memory bandwidth and build |
| GPU acceleration | Vendor/backend-specific support (for example CUDA, ROCm, Metal and Vulkan paths); verify exact hardware and driver matrix | Multiple backends including CUDA, HIP/ROCm, Metal, Vulkan, SYCL and others; verify feature matrix for the exact backend |
| Hybrid CPU/GPU | Scheduler can place model work across available CPU/GPU memory according to supported backend and available memory | Supports CPU/GPU layer offload, allowing partial GPU acceleration when weights do not fit entirely in VRAM |
| Serving interface | Local HTTP API, including generate/chat endpoints | `llama-server` HTTP API and web UI; OpenAI-compatible chat, responses and embeddings routes documented |
| Operational complexity | Generally simpler model acquisition and first-run workflow | More control over build flags, backend, model file, context, threads and offload; more tuning responsibility |
| Resource controls | Environment/API controls for model keep-alive, queue size, loaded models and parallel requests | Explicit runtime parameters for context, CPU threads, device selection and GPU layers; exact controls depend on build/version |
| Main evaluation risk | Do not assume a convenient local API means production-ready multi-user security or capacity | Backend/model compatibility and tuning vary; do not assume every model feature is equally supported on every backend |

### Preliminary interpretation

- Ollama is a strong candidate for a low-friction local developer trial, subject to exact platform and operational checks.
- llama.cpp is a strong candidate when GGUF quantization, CPU-first execution, backend choice and CPU/GPU layer offload are important.
- This comparison does not establish a winner. Task 10 owns the final evaluation and approval.

## 3. Hardware inventory required

Complete this inventory for the actual intended inference host before making a machine-specific recommendation.

| Field | Required evidence | Current value |
|---|---|---|
| Device role | Developer laptop, desktop, workstation, dedicated server or mobile device | Unknown |
| Operating system | Name, version, architecture, kernel/build | Unknown |
| CPU | Exact model, architecture, physical/logical cores, supported instruction sets | Unknown |
| System RAM | Installed, currently available and practical headroom | Unknown |
| GPU / iGPU | Exact vendor and model; integrated or discrete | Unknown |
| GPU memory | Dedicated VRAM; shared/unified memory where applicable | Unknown |
| Driver / backend | Driver version and compatible CUDA/ROCm/Metal/Vulkan/SYCL stack | Unknown |
| Storage | Free space on model/cache volume; filesystem and permissions | Unknown |
| Power / thermal | Sustained power limit, cooling and throttling behavior | Unknown |
| Deployment role | Single-user local test or always-on multi-user host | Unknown |
| Concurrency | Expected simultaneous requests | Unknown |
| Latency target | Time-to-first-token and generation throughput objective | Unknown |
| Network boundary | Loopback-only, private LAN or isolated server network | Unknown |

Do not infer CPU, RAM, GPU, storage or model-host capacity from the fact that development is currently performed on a phone.

## 4. Memory sizing method

A model's download/package size is not its total runtime memory requirement.

Estimate total memory using separate components:

1. **Model weights:** determined by parameter count, precision/quantization and actual artifact layout.
2. **KV cache:** depends on architecture, context length, cache precision and concurrent sequences. Increasing context or parallel requests can materially increase memory.
3. **Runtime/backend buffers:** temporary tensors, graph/workspace buffers, memory mapping and backend-specific allocations.
4. **Operating-system and application headroom:** OS, API process, orchestration, monitoring and other applications.
5. **Safety margin:** leave headroom for fragmentation, peak allocations and normal system activity.

For GPU inference, assess VRAM and whether the runtime can offload layers to system RAM/CPU. For CPU inference, assess available system RAM and memory bandwidth. Unified-memory systems need their own platform-specific assessment; do not count all installed memory as freely available to the model.

No universal minimum RAM/VRAM number is declared in this document. A valid minimum must name the exact model revision, quantization, runtime version, context size, concurrency and target operating system, then be verified on the target hardware.

## 5. Runtime-specific research notes

### Ollama

Official documentation reviewed:

- GPU support is backend- and hardware-specific. Check the current GPU support documentation and exact driver requirements for the target device.
- The FAQ documents model placement across CPU/GPU and the `ollama ps` processor field for inspecting placement.
- Model storage location is configurable; storage permissions and free disk space must be checked.
- Keep-alive, queue limits, loaded-model limits and parallel request settings affect resource use and scheduling.
- Parallel requests can multiply effective context/KV-cache memory demand. Do not extrapolate single-request memory to concurrent production use.

Sources:
- https://github.com/ollama/ollama/blob/main/docs/faq.mdx
- https://github.com/ollama/ollama/blob/main/docs/gpu.mdx
- https://github.com/ollama/ollama/blob/main/docs/context-length.mdx

### llama.cpp

Official documentation reviewed:

- The project supports GGUF models and quantization options from very low-bit formats through 8-bit formats; quality and speed must be tested for the exact model/quantization.
- Supported backends include CPU, CUDA, HIP, Metal, Vulkan, SYCL and additional platform-specific options. Feature coverage differs by backend.
- CPU/GPU hybrid inference can offload some layers to GPU while keeping other work in system memory.
- `llama-server` provides HTTP endpoints and documents OpenAI-compatible chat, responses and embeddings routes, parallel decoding and continuous batching.
- Build options, device selection, context size and thread configuration need to be pinned in benchmark records.

Sources:
- https://github.com/ggml-org/llama.cpp
- https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md
- https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- https://github.com/ggml-org/llama.cpp/wiki/Feature-matrix

## 6. Security and operations readiness

Before any local server is exposed beyond the host:

- Keep inference endpoints bound to loopback/private interfaces unless a reviewed network design requires otherwise.
- Do not assume a local inference endpoint provides user authentication or tenant authorization; enforce those at the BIRAJ AI service boundary.
- Never expose model-server credentials, API keys or environment secrets to client apps or logs.
- Restrict model directories and runtime process permissions; verify downloaded artifact provenance and checksums where available.
- Pin runtime version, model revision, quantization and backend build options for reproducibility.
- Define startup/shutdown, health/readiness, overload behavior, request queue limits and resource exhaustion handling.
- Do not silently fall back to a hosted model API when the local runtime is unavailable.
- Preserve diagnostic evidence while redacting secrets and user-sensitive prompt content according to the project's logging policy.

## 7. Readiness classification

| State | Meaning | Evidence required |
|---|---|---|
| Ready for controlled test | Host, drivers, storage and memory headroom are known and a specific test configuration fits | Complete inventory plus model/runtime-specific sizing and controlled test plan |
| Constrained / CPU-only | No suitable accelerator path, but system RAM/CPU may support a small controlled test | Exact CPU/RAM inventory and realistic throughput target |
| Not ready | Known hardware or platform constraints prevent the proposed test | Reproducible incompatibility or insufficient resource evidence |
| Unknown | Required host information is missing | Inventory remains incomplete; do not guess |

**Current classification: Unknown.** The intended inference host has not been identified and its hardware specifications have not been supplied.

## 8. Acceptance checklist

- [x] Hardware inventory template is complete; actual inference-host values remain unknown.
- [x] Ollama and llama.cpp comparison is supported by official project documentation.
- [x] Memory-sizing components and context/concurrency effects are documented.
- [x] CPU fallback, accelerator support and backend caveats are stated without universal guarantees.
- [x] Security and operational controls are documented.
- [x] Unknown hardware fields remain explicitly unknown.
- [x] No model/runtime selection, install, download, live inference, paid infrastructure or purchase has occurred.
- [x] Research has been reviewed and linked from Notion Task 20.

## 9. Open questions

- What exact machine is intended to host BIRAJ AI inference?
- Is the first target a local single-user test host or a separate always-on server?
- What concurrency and latency target should be used for the eventual serving evaluation?
- Which operating system and accelerator driver stack can be supported and maintained?

Until these are answered, a machine-specific runtime recommendation and real performance estimate are blocked.

## 10. Related project records

- Notion Task 20: https://app.notion.com/p/40e3080827b38183a0acf42a2227aa88
- Parent Notion Task 10: https://app.notion.com/p/40e3080827b381648db0e823d4c6b2c9
- Existing architecture baseline: [ARCHITECTURE.md](ARCHITECTURE.md)
- Model/runtime evaluation: [MODEL-EVALUATION.md](MODEL-EVALUATION.md)


## 11. Review addendum — 2026-11-05

A second-pass review of the official llama.cpp server documentation confirms several operational details relevant to any future adapter:

- The documented default `llama-server` listener is `127.0.0.1:9931`, which is loopback-only. The Docker example explicitly changes the bind address to `0.0.0.0`; that changes the exposure boundary and must not be copied into a deployment without a reviewed network and authentication design.
- The server documents OpenAI-compatible chat-completions, responses and embeddings routes, parallel decoding, multi-user support, continuous batching, monitoring endpoints and schema-constrained JSON output. These are runtime capabilities, not guarantees that every model/backend supports every feature identically.
- The project documents CPU and GPU inference for F16 and quantized models, multiple quantization levels, and CPU/GPU hybrid inference. Exact performance and feature coverage remain build-, backend-, model- and hardware-dependent.
- The future BIRAJ adapter must normalize capabilities and errors rather than assuming feature parity. It should expose a capability snapshot (for example streaming, structured output, embeddings and parallel generation) and reject unsupported requested features explicitly.

Additional official references reviewed:
- llama.cpp server API and default listener: https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md
- llama.cpp quantization and backend overview: https://github.com/ggml-org/llama.cpp

This review does not select llama.cpp or authorize installation, model download, inference, network exposure or production deployment. Task 10 remains responsible for final model/runtime evaluation. The actual inference-host inventory remains Unknown.
