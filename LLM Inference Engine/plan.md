# LLM Inference Engine — Build Plan

Self-hosted, OpenAI-API-compatible inference server. Built as an orchestration
layer over **llama.cpp** (GGUF, CPU/GPU) with a second **AWQ** backend added
later, unified behind one FastAPI service.

Tech stack: FastAPI, `llama-cpp-python` (GGUF), `autoawq` + PyTorch (AWQ),
Pydantic, SSE for streaming, Docker for packaging.

---

## Phase 1 — Core Server & Single-Model Inference

Goal: a working server that loads one GGUF model and answers one request at a time.

- Project scaffold: `app/` package, `pyproject.toml`/`requirements.txt`, config via env vars (model path, context length, threads/GPU layers).
- Model wrapper around `llama-cpp-python`: load a GGUF model, expose `generate(prompt, params)`.
- FastAPI app with OpenAI-compatible schemas (Pydantic models matching the real `/v1/chat/completions` and `/v1/completions` request/response shapes).
- Non-streaming chat + completion endpoints, synchronous, one request in flight.
- Prompt templating per model family (Llama/Mistral/Qwen/Gemma chat templates).
- Basic error handling (bad params, model not loaded, context overflow) as OpenAI-style error JSON.

**Acceptance:** `curl` a chat completion against a local GGUF model and get a correct, non-streamed response using the official OpenAI request format.

---

## Phase 2 — Streaming, Multi-Model, Token Stats

Goal: match real client expectations — streaming tokens, more than one model, usage accounting.

- SSE streaming for `stream=true` on both endpoints, chunked deltas matching OpenAI's format, proper `[DONE]` sentinel.
- Model registry: multiple named GGUF models declared in config; lazy load on first request, LRU unload under a memory budget.
- `/v1/models` endpoint listing loaded/available models.
- Token statistics: prompt tokens, completion tokens, total tokens in every response; time-to-first-token and tokens/sec logged and returned in a debug field.
- Structured logging per request (model, latency, token counts).

**Acceptance:** switch models by name in the request body, stream a response token-by-token, and see accurate usage stats on both streamed and non-streamed calls.

---

## Phase 3 — KV Cache & Continuous Batching

Goal: serve concurrent requests efficiently instead of one-at-a-time.

- Session/slot manager: map in-flight requests to llama.cpp context slots so KV cache is reused correctly and not clobbered across concurrent calls.
- Request queue + scheduler: collect pending prompts and step them together each generation tick (continuous batching), instead of serial FIFO processing.
- Backpressure: max concurrent slots, queue depth limit, request timeouts, 429 on overload.
- Cancellation: client disconnect stops generation and frees the slot/cache.
- Load test harness (concurrent requests) to verify throughput scales with batching and KV cache isn't corrupted under concurrency.

**Acceptance:** N concurrent streaming requests complete correctly and faster in aggregate than N sequential requests, with no cross-request output contamination.

---

## Phase 4 — AWQ Backend, Metrics, Hardening & Packaging

Goal: second quantization backend, production-grade observability, ship it.

- AWQ backend using PyTorch + `autoawq`, implementing the same internal `generate`/streaming interface as the GGUF backend, selectable per model in the registry.
- `/metrics` endpoint (Prometheus format): request counts, latency histograms, tokens/sec, active slots, queue depth.
- Health/readiness endpoints for orchestration (`/healthz`, `/readyz`).
- Auth (API key header) and rate limiting.
- Test suite: unit tests for schema/templating, integration tests against a small GGUF model, load test for Phase 3 guarantees.
- Dockerfile + docker-compose (CPU and GPU variants), README with setup/run instructions and example `curl`/OpenAI-SDK usage.

**Acceptance:** `docker compose up` serves both a GGUF and an AWQ model through the same API, with metrics, auth, and passing tests.

---

## Out of scope (for now)

- Writing custom CUDA/Triton kernels or a from-scratch transformer forward pass — leaning on llama.cpp/PyTorch for the math.
- Distributed multi-GPU tensor/pipeline parallelism.
- Fine-tuning/training support.
