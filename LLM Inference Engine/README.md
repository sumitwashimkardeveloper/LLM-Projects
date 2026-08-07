# LLM Inference Engine

A **production-ready, self-hosted inference server** that provides OpenAI-API-compatible endpoints for running large language models locally. Deploy quantized models with multi-backend support, built-in authentication, rate limiting, and comprehensive observability.

## 🎯 Project Overview

This is **Phase 4** of the development roadmap — production-grade hardening. The inference engine is designed to serve multiple models simultaneously with high throughput, low latency, and complete API compatibility with OpenAI's API.

**Key Capability**: Run open-source LLMs locally without cloud dependencies, with enterprise-grade features like metrics, authentication, rate limiting, and health checks.

## 🚀 Quick Setup

### Prerequisites
- Python 3.10+
- CUDA 11.8+ (for GPU support) OR CPU-only mode
- 8GB+ RAM (16GB+ recommended)
- Disk space for models (varies by model size)

### Installation

#### 1. Base Installation
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate
# OR Activate (Linux/Mac)
source .venv/bin/activate

# Install core dependencies
pip install -r requirements.txt
```

#### 2. GPU Support (Optional)
For NVIDIA GPU acceleration with AWQ backend:
```bash
pip install -r requirements-awq.txt
```

#### 3. Development Setup
For running tests and development tools:
```bash
pip install -r requirements-dev.txt
```

## ⚙️ Configuration

### Quick Configuration Setup

```bash
# Create configuration files from examples
cp .env.example .env
cp models.json.example models.json

# Edit with your settings
# .env contains server and security config
# models.json contains model registry
```

### Multi-Model Registry (`models.json`)

Define all models you want to serve:

```json
{
  "models": [
    {
      "name": "llama-3-8b",
      "path": "/models/llama-3-8b-instruct-q4.gguf",
      "family": "llama3",
      "backend": "gguf",
      "n_ctx": 8192,
      "n_parallel": 2,
      "n_gpu_layers": 33
    },
    {
      "name": "mistral-7b",
      "path": "/models/mistral-7b-instruct-awq.safetensors",
      "family": "mistral",
      "backend": "awq",
      "device": "cuda:0",
      "n_parallel": 4
    }
  ]
}
```

**Model Configuration Keys:**
| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `name` | string | ✓ | Model identifier for API requests |
| `path` | string | ✓ | Full filesystem path to model file |
| `family` | string | ✓ | Prompt template: `llama3`, `mistral`, `qwen`, `gemma`, `auto` |
| `backend` | string | ✓ | `gguf` (CPU/GPU) or `awq` (GPU only) |
| `n_ctx` | integer | ✗ | Context window size; inherits from `N_CTX` env var |
| `n_parallel` | integer | ✗ | Concurrent request slots; inherits from `N_PARALLEL` |
| `n_gpu_layers` | integer | ✗ | GGUF only: layers to offload to GPU |
| `device` | string | ✗ | AWQ only: CUDA device identifier |

### Environment Variables

#### Model Loading
```env
# Multi-model mode (recommended)
MODELS_MANIFEST=./models.json

# Single-model fallback (if models.json not found)
MODEL_PATH=/path/to/model.gguf
MODEL_NAME=my-model
MODEL_FAMILY=llama3

# Context window
N_CTX=4096

# GPU layers (GGUF only)
N_GPU_LAYERS=33
```

#### Concurrency & Performance
```env
# Concurrent request slots per model
N_PARALLEL=2

# Maximum models to keep loaded in memory
MAX_LOADED_MODELS=1

# Maximum queued requests before rejection
MAX_QUEUE_DEPTH=64

# Request timeout (seconds)
REQUEST_TIMEOUT_S=120
```

#### GPU (AWQ Backend)
```env
# CUDA device for AWQ models
AWQ_DEVICE=cuda:0

# Data type: float16 or bfloat16
AWQ_DTYPE=float16
```

#### Security
```env
# API keys (comma-separated; empty to disable)
API_KEYS=sk-prod-key-here,sk-test-key-here

# Rate limiting (requests/minute per IP; 0 to disable)
RATE_LIMIT_RPM=60
```

#### Server
```env
# Bind address
HOST=0.0.0.0
PORT=8000

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

### Configuration Example

Complete `.env` file:
```env
# Server
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=production

# Model Loading
MODELS_MANIFEST=./models.json
N_CTX=4096
N_GPU_LAYERS=33
N_PARALLEL=2

# Concurrency
MAX_LOADED_MODELS=2
MAX_QUEUE_DEPTH=64
REQUEST_TIMEOUT_S=120

# GPU (if using AWQ)
AWQ_DEVICE=cuda:0
AWQ_DTYPE=float16

# Security
API_KEYS=sk-your-key-here
RATE_LIMIT_RPM=60

# Logging
LOG_LEVEL=INFO
```

## 🏃 Running the Server

### Development Mode
Fast development with auto-reload:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server runs at `http://localhost:8000`

### Production Mode (with Gunicorn)
Production-grade deployment with multiple workers:
```bash
pip install gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
```

Adjust worker count (`-w`) based on CPU cores.

### Docker Deployment

#### CPU-Only (Smaller image)
```bash
docker build -t llm-inference:cpu -f Dockerfile .
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/.env:/app/.env \
  llm-inference:cpu
```

#### GPU with Docker Compose (Recommended)
```bash
# Start GPU inference service
docker-compose up inference-gpu

# Scale to multiple GPU devices
docker-compose up --scale inference-gpu=2
```

#### View Logs
```bash
docker logs -f llm-inference
# Or with compose
docker-compose logs -f inference-gpu
```

### Health Check
```bash
curl http://localhost:8000/health
# Returns: {"status": "ok", "models_loaded": 1, "uptime": 123.45}
```

## 📡 API Endpoints

All endpoints follow **OpenAI API v1 specification** for compatibility.

### Chat Completions (Streaming & Non-Streaming)
```http
POST /v1/chat/completions
```

**Request:**
```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "llama-3-8b",
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "Explain quantum computing"}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }'
```

**Response:**
```json
{
  "id": "chatcmpl-8Xy...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "llama-3-8b",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Quantum computing uses quantum bits..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 28,
    "completion_tokens": 156,
    "total_tokens": 184
  }
}
```

### Streaming Chat Completions
Same endpoint as above with `"stream": true`. Responses as Server-Sent Events (SSE):

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{"model": "llama-3-8b", "messages": [...], "stream": true}'
```

### Text Completions
```http
POST /v1/completions
```

**Request:**
```bash
curl -X POST http://localhost:8000/v1/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-your-api-key" \
  -d '{
    "model": "mistral-7b",
    "prompt": "The capital of France is",
    "max_tokens": 10
  }'
```

### List Available Models
```http
GET /v1/models
```

**Response:**
```json
{
  "object": "list",
  "data": [
    {
      "id": "llama-3-8b",
      "object": "model",
      "owned_by": "local",
      "created": 1234567890
    }
  ]
}
```

### Metrics (Prometheus Format)
```http
GET /metrics
```

Returns Prometheus-compatible metrics:
```
# HELP inference_requests_total Total requests
# TYPE inference_requests_total counter
inference_requests_total{model="llama-3-8b",endpoint="/v1/chat/completions"} 42
```

### Health Checks
```http
GET /health
GET /healthz
GET /readyz
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "models_loaded": 1,
  "timestamp": "2024-08-08T10:30:45Z",
  "uptime_seconds": 3600
}
```

### System Status
```http
GET /v1/system/status
```

Returns detailed system information and model statistics.

## 🐍 Python Client Examples

### Using OpenAI SDK

Since the inference engine is OpenAI-API-compatible, use the official Python client:

```bash
pip install openai
```

#### Non-Streaming Chat Completion
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="sk-your-api-key"  # or leave empty if not configured
)

response = client.chat.completions.create(
    model="llama-3-8b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ],
    temperature=0.7,
    max_tokens=256
)

print(response.choices[0].message.content)
```

#### Streaming Chat Completion
```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1")

stream = client.chat.completions.create(
    model="llama-3-8b",
    messages=[{"role": "user", "content": "Count to 10"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

#### Multiple Models
```python
# List available models
models = client.models.list()
for model in models.data:
    print(f"- {model.id}")

# Use different models
for model_name in ["llama-3-8b", "mistral-7b"]:
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": "Hello"}]
    )
    print(f"{model_name}: {response.choices[0].message.content}")
```

#### Error Handling
```python
from openai import APIError, RateLimitError, AuthenticationError

try:
    response = client.chat.completions.create(
        model="unknown-model",
        messages=[{"role": "user", "content": "Hi"}]
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded, retry later")
except APIError as e:
    print(f"API error: {e}")
```

## ⚡ Key Features

### Multi-Backend Support
- **GGUF** (llama.cpp) — CPU and GPU inference with quantized models
  - Supports: Llama, Mistral, Qwen, Gemma, and more
  - Layer offloading to GPU with `N_GPU_LAYERS`
- **AWQ** (PyTorch) — GPU-optimized tensor quantization
  - Faster inference on NVIDIA GPUs
  - Per-model CUDA device configuration

### Concurrency & Scheduling
- **Per-Model Slot Pool** — `N_PARALLEL` independent inference contexts
- **Continuous Batching** — Multiple requests to same model progress together
- **Backpressure Handling** — Queue-depth limits with 429 responses on overload
- **Request Timeouts** — 408 responses for requests queued too long
- **Stream Cancellation** — Disconnect cleanly stops token generation

### Observability & Monitoring
- **Prometheus Metrics** (`/metrics`) — Request counts, latency histograms (p50/p95/p99), tokens/sec
- **Structured Logging** — Request ID, model, endpoint, token counts, latency
- **Health Checks** — Multiple endpoints for container orchestration
- **System Status** — Detailed model and resource information

### Authentication & Rate Limiting
- **API Key Validation** — Bearer token in Authorization header
- **Per-IP Rate Limiting** — Configurable requests-per-minute limits
- **Error Responses** — 401 for auth failures, 429 for rate limits
- **Key Rotation** — Simple key management

### Production Deployment
- **Multi-Container Architecture** — Docker, Docker Compose, Kubernetes-ready
- **Health Probes** — Liveness and readiness checks
- **Graceful Shutdown** — Complete in-flight requests before stopping
- **Resource Limits** — Memory and GPU management

### Testing & Quality
```bash
# Unit tests for schemas, templates, auth
pytest tests/ -v

# With coverage report
pytest tests/ --cov=app --cov-report=html

# API endpoint tests only
pytest tests/test_api.py -v
```

## 📁 Project Structure

```
LLM Inference Engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── logger.py               # Logging setup
│   ├── models/
│   │   ├── base.py            # Base model interface
│   │   ├── gguf.py            # GGUF backend (llama.cpp)
│   │   └── awq.py             # AWQ backend (GPU)
│   ├── routes/
│   │   ├── chat.py            # Chat completions endpoints
│   │   ├── completions.py     # Text completion endpoints
│   │   └── health.py          # Health and metrics
│   ├── schemas/               # Pydantic models
│   ├── services/              # Business logic
│   │   ├── model_loader.py
│   │   ├── inference.py
│   │   └── metrics.py
│   └── utils/                 # Helpers
│
├── tests/
│   ├── test_api.py
│   ├── test_schemas.py
│   └── test_auth.py
│
├── Dockerfile                  # CPU image
├── Dockerfile.gpu             # GPU image (CUDA)
├── docker-compose.yml         # Multi-service compose
├── .dockerignore
├── requirements.txt           # Core dependencies
├── requirements-awq.txt       # GPU dependencies
├── requirements-dev.txt       # Dev/test dependencies
├── .env.example
├── models.json.example
├── plan.md                    # Development roadmap
└── README.md                  # This file
```

## 🏗️ Architecture Notes

### Design Philosophy
This is a **scheduling-level orchestration layer** over existing inference engines, not a low-level inference framework.

### What's Included
- ✅ Multi-model scheduling and loading
- ✅ Per-model slot pooling (continuous batching)
- ✅ Queue management with backpressure
- ✅ API compatibility with OpenAI
- ✅ Metrics and monitoring
- ✅ Authentication and rate limiting

### What's Not Included
- ❌ Distributed multi-GPU tensor parallelism (would require FSDP/DeepSpeed)
- ❌ Model fine-tuning (see Fine-Tuning Studio)
- ❌ Fused-batch decoding at CUDA kernel level
- ❌ Custom model training

### Memory Considerations
Each `N_PARALLEL` slot requires a full copy of model weights:
- Example: 4GB Q4 GGUF with `N_PARALLEL=4` = ~16GB total memory needed
- AWQ models typically use less memory than GGUF due to efficient quantization

### Concurrency Model
- **Single Python daemon thread** schedules slot stepping (one token at a time)
- **Different models** can generate concurrently (separate schedulers)
- **Same model** requests batch together in one scheduler
- **Stream cancellation** on disconnect stops generation mid-token

### Streaming
- Server-Sent Events (SSE) protocol
- Fully compatible with OpenAI's `stream=true` format
- Clients can disconnect to cancel mid-stream

## 🔧 Troubleshooting

### GPU Not Detected
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"

# Verify CUDA device
python -c "import torch; print(torch.cuda.get_device_name(0))"
```

### Out of Memory (OOM)
- Reduce `N_PARALLEL` or `MAX_LOADED_MODELS`
- Use quantized models (Q4, Q5 instead of full precision)
- Reduce `N_CTX` (context window size)
- Use AWQ backend for more efficient GPU memory usage

### Slow Model Loading
- First load is slow (reads from disk)
- Consider using faster storage (NVMe SSD)
- Keep 1-2 most-used models loaded in memory

### Connection Timeouts
- Increase `REQUEST_TIMEOUT_S` for long queries
- Check network connectivity if using remote deployment
- Monitor server logs for errors

## 📊 Performance Tuning

### For CPU Inference
- Set `N_PARALLEL=1` (CPU doesn't parallelize well)
- Increase `N_CTX` moderately (16K possible on 16GB RAM)
- Use Q4 or Q5 quantization

### For GPU Inference (GGUF)
- Set `N_GPU_LAYERS=33+` (offload most to GPU)
- Increase `N_PARALLEL` based on VRAM (2-8 typically)
- Use Q4_KM quantization for quality/speed balance

### For GPU Inference (AWQ)
- Set `N_PARALLEL` higher (4-16 depending on model and VRAM)
- AWQ is inherently more efficient than GGUF
- Use `bfloat16` for better accuracy if VRAM permits

## 📖 Additional Resources

- [plan.md](./plan.md) — Complete 4-phase development roadmap
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [llama.cpp Documentation](https://github.com/ggerganov/llama.cpp)
- [AWQ Documentation](https://github.com/mit-han-lab/llm-awq)

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## 💬 Support

- **GitHub Issues** — Report bugs and request features
- **Discussions** — Ask questions and share ideas
- **Documentation** — Check plan.md for implementation details
