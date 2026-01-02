# LLM Inference Engine

Self-hosted, OpenAI-API-compatible inference server. See [plan.md](plan.md)
for the full four-phase build plan. This is **Phase 3**: concurrent request
handling per model via a slot-based scheduler, with backpressure and
stream-cancellation.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Download one or more GGUF models (e.g. from Hugging Face) into `models/`,
then declare them:

```bash
copy .env.example .env
copy models.json.example models.json
# edit models.json: name, path, and family ("llama3" | "mistral" | "qwen" | "gemma" | "auto")
```

`MAX_LOADED_MODELS` in `.env` caps how many models stay resident in memory
at once; models load lazily on first request and the least-recently-used
one is evicted once the cap is exceeded. If you only ever want one model
and don't want to bother with `models.json`, delete/rename it and set
`MODEL_PATH`/`MODEL_NAME`/`MODEL_FAMILY` in `.env` instead — that's used as
a one-model fallback when the manifest file isn't found.

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Try it

```bash
curl http://localhost:8000/health
curl http://localhost:8000/v1/models

curl http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"llama-3-8b-instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"Say hi in five words.\"}]}"

curl http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"llama-3-8b-instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"Count to 5.\"}], \"stream\": true}"

curl http://localhost:8000/v1/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"qwen2.5-7b-instruct\", \"prompt\": \"The capital of France is\", \"max_tokens\": 16}"
```

Or with the official OpenAI Python SDK, pointed at the local server:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8000/v1", api_key="not-needed")

resp = client.chat.completions.create(
    model="llama-3-8b-instruct",
    messages=[{"role": "user", "content": "Say hi in five words."}],
)
print(resp.choices[0].message.content)

stream = client.chat.completions.create(
    model="llama-3-8b-instruct",
    messages=[{"role": "user", "content": "Count to 5."}],
    stream=True,
)
for chunk in stream:
    if chunk.choices and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

## What's implemented (Phase 3)

- `stream=true` on both `/v1/chat/completions` and `/v1/completions` —
  Server-Sent Events with incremental deltas and a trailing `data: [DONE]`
- Multi-model registry (`models.json`) with lazy loading + LRU eviction
- `GET /v1/models`, `usage`, and `timing` on every response (Phase 2)
- Per-model slot pool (`BatchScheduler` in `app/scheduler.py`): each model
  gets `n_parallel` independent llama.cpp contexts ("slots"), each with its
  own KV cache. A background thread admits queued requests into free slots
  and steps every busy slot's generation one token at a time in round-robin
  order, so multiple requests to the *same* model make progress
  concurrently instead of queuing fully serially
- Backpressure: `MAX_QUEUE_DEPTH` caps how many requests can wait for a
  free slot (further requests get `429 overloaded`); `REQUEST_TIMEOUT_S`
  fails a request that's been queued too long (`408 timeout`)
- Cancellation: if a streaming client disconnects, the slot is freed and
  generation stops instead of burning compute for an abandoned request

`n_parallel` is configurable per model in `models.json` (falls back to
`N_PARALLEL` in `.env`). Each slot loads an independent copy of the model
weights, so raising it trades memory for concurrency — a 4GB Q4 model with
`n_parallel: 4` uses roughly 16GB. This is a scheduling-level form of
concurrency (independent contexts sharing time on the same thread); true
fused-batch decoding across sequences in a single forward pass (what
vLLM/llama.cpp's own server do at the CUDA-kernel level) would need the
low-level `llama_batch`/`llama_decode` API and is out of scope here.
