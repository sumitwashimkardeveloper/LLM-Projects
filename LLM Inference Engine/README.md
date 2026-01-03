# LLM Inference Engine

Self-hosted, OpenAI-API-compatible inference server with multi-backend support,
metrics, auth, and rate-limiting. See [plan.md](plan.md) for the full
four-phase build plan. This is **Phase 4**: production-grade hardening.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

For AWQ backend support:
```bash
pip install -r requirements-awq.txt
```

For development and testing:
```bash
pip install -r requirements-dev.txt
```

## Configuration

Copy example files and edit for your setup:

```bash
cp .env.example .env
cp models.json.example models.json
```

### Multi-Model Registry (`models.json`)

Each model entry specifies:
- `name`: identifier for requests
- `path`: filesystem path to the model file
- `family`: prompt template ("llama3" | "mistral" | "qwen" | "gemma" | "auto")
- `backend`: "gguf" (llama.cpp) or "awq" (GPU tensor-based quantization)
- `n_ctx`: context window (optional; inherits from `N_CTX`)
- `n_parallel`: concurrent slots per model (optional; inherits from `N_PARALLEL`)
- `device`: for AWQ backend, e.g., "cuda:0" (optional; inherits from `AWQ_DEVICE`)

### Environment Variables

**Model Loading**
- `MODELS_MANIFEST`: path to `models.json`; if not found, falls back to single-model mode
- `MODEL_PATH`, `MODEL_NAME`, `MODEL_FAMILY`: single-model fallback
- `N_CTX`: context window (default 4096)
- `N_GPU_LAYERS`: GGUF only; layers to offload to GPU (default 0)

**Concurrency**
- `N_PARALLEL`: slots per model (default 2; ~4GB per GGUF copy)
- `MAX_LOADED_MODELS`: resident models before LRU eviction (default 1)
- `MAX_QUEUE_DEPTH`: requests queued before rejecting (default 64)
- `REQUEST_TIMEOUT_S`: fail requests queued too long (default 120)

**AWQ Backend (GPU)**
- `AWQ_DEVICE`: CUDA device, e.g., "cuda:0" (default "cuda:0")
- `AWQ_DTYPE`: "float16" or "bfloat16" (default "float16")

**Security**
- `API_KEYS`: comma-separated keys; empty to disable (default "")
- `RATE_LIMIT_RPM`: requests/minute per client IP; 0 to disable (default 0)

**Server**
- `HOST`, `PORT`: bind address (default 0.0.0.0:8000)

## Run

**Development:**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production (with gunicorn):**
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

**Docker (CPU):**
```bash
docker build -t llm-inference:cpu .
docker run -p 8000:8000 -v $(pwd)/models:/app/models llm-inference:cpu
```

**Docker (GPU with docker-compose):**
```bash
docker-compose up inference-gpu
```

## API Endpoints

### Chat Completions
```bash
curl http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "llama-3-8b-instruct",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

### Completions (raw prompt)
```bash
curl http://localhost:8000/v1/completions \
  -H "Authorization: Bearer your-api-key" \
  -d '{"model": "qwen2.5-7b-instruct", "prompt": "The capital of France is"}'
```

### List Models
```bash
curl http://localhost:8000/v1/models
```

### Metrics (Prometheus format)
```bash
curl http://localhost:8000/metrics
```

### Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/healthz
curl http://localhost:8000/readyz
```

## OpenAI SDK

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="your-api-key"  # if configured
)

# Non-streaming
resp = client.chat.completions.create(
    model="llama-3-8b-instruct",
    messages=[{"role": "user", "content": "Count to 5"}],
)
print(resp.choices[0].message.content)

# Streaming
stream = client.chat.completions.create(
    model="qwen2.5-7b-instruct",
    messages=[{"role": "user", "content": "Explain AI in one sentence"}],
    stream=True,
)
for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## Phase 4 Features

### Multi-Backend Support
- **GGUF** (llama.cpp): CPU-friendly, quantized models (Llama, Mistral, Qwen, Gemma)
- **AWQ** (PyTorch): GPU tensor-based quantization; select per model in `models.json`

### Concurrency & Scheduling (Phase 3)
- Per-model slot pool: `N_PARALLEL` independent llama.cpp/AWQ contexts
- Continuous batching: multiple requests to same model make progress together
- Backpressure: queue-depth limits (429 on overload), request timeouts (408)
- Cancellation: disconnect stops generation mid-stream

### Metrics & Observability (Phase 4)
- Prometheus endpoint (`/metrics`): request counts, latency histograms (p95/mean),
  tokens generated, tokens/sec
- Structured logging: request ID, model, endpoint, token counts, latency

### Authentication & Rate-Limiting (Phase 4)
- API key validation (Bearer token in Authorization header)
- Per-IP rate limiting (requests per minute)
- 401 on invalid auth, 429 on rate limit exceeded

### Production Packaging
- Dockerfile (CPU, Python slim base)
- Dockerfile.gpu (CUDA 12.1, AWQ support)
- docker-compose.yml (CPU and GPU services, healthchecks)
- .dockerignore (exclude models, test artifacts, .git)

### Testing
```bash
pytest tests/                    # Unit tests (schemas, templates, auth)
pytest tests/ -v --cov=app      # With coverage
pytest tests/test_api.py         # API endpoint tests only
```

## Architecture Notes

- **Not included**: distributed multi-GPU tensor parallelism, fine-tuning,
  fused-batch decoding at the CUDA kernel level (would need llama.cpp's
  low-level `llama_batch`/`llama_decode` API). This is a scheduling-level
  orchestration layer over existing engines, not a low-level inference
  framework.
- **Memory per slot**: each `N_PARALLEL` slot loads a full copy of the model
  weights. A 4GB Q4 GGUF with `N_PARALLEL=4` uses ~16GB.
- **Concurrency scope**: slots are scheduled in a single Python daemon thread,
  stepping one token at a time. Two different models can generate concurrently
  (separate schedulers); two requests to the same model batch in one scheduler.
- **Streaming**: Server-Sent Events (SSE), matching OpenAI's `stream=true` format.
