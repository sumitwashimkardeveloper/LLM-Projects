# LLM Inference Engine

Self-hosted, OpenAI-API-compatible inference server. See [plan.md](plan.md)
for the full four-phase build plan. This is **Phase 2**: streaming, a
multi-model registry with lazy loading + LRU eviction, and token/timing
stats on every response.

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

## What's implemented (Phase 2)

- `stream=true` on both `/v1/chat/completions` and `/v1/completions` —
  Server-Sent Events with incremental deltas and a trailing `data: [DONE]`,
  matching OpenAI's chunk format
- Multi-model registry (`models.json`): models load lazily on first
  request; once more than `MAX_LOADED_MODELS` are resident, the
  least-recently-used one is evicted
- `GET /v1/models` — lists configured models and whether each is
  currently loaded
- `usage` (prompt/completion/total tokens) on every response, streamed or
  not — on streams it arrives as a final chunk before `[DONE]`
- `timing` field (`time_to_first_token_ms`, `tokens_per_sec`) on every
  response — a non-standard extension, not part of the OpenAI schema
- Structured request logging (request id, model, endpoint, token counts,
  latency, tokens/sec) to stdout

Everything still runs one generation at a time per model (two different
models can generate concurrently since each has its own engine, but two
requests to the *same* model queue up). Real intra-model concurrency
(continuous batching, per-request KV cache slots) is Phase 3.
