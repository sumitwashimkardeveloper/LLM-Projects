# LLM Inference Engine

Self-hosted, OpenAI-API-compatible inference server. See [plan.md](plan.md)
for the full four-phase build plan. This is **Phase 1**: single-model,
non-streaming chat/completion over a GGUF model via `llama-cpp-python`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Download a GGUF model (e.g. from Hugging Face) into `models/`, then:

```bash
copy .env.example .env
# edit .env: set MODEL_PATH to your .gguf file, MODEL_NAME to whatever you want
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Try it

```bash
curl http://localhost:8000/health

curl http://localhost:8000/v1/chat/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"llama-3-8b-instruct\", \"messages\": [{\"role\": \"user\", \"content\": \"Say hi in five words.\"}]}"

curl http://localhost:8000/v1/completions ^
  -H "Content-Type: application/json" ^
  -d "{\"model\": \"llama-3-8b-instruct\", \"prompt\": \"The capital of France is\", \"max_tokens\": 16}"
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
```

## What's implemented (Phase 1)

- `POST /v1/chat/completions` — non-streaming, OpenAI-compatible schema
- `POST /v1/completions` — non-streaming, raw-prompt completion
- `GET /health`
- Chat prompt templating for Llama 3, Mistral, Qwen (ChatML), Gemma, with a
  ChatML fallback for unrecognized models — set `MODEL_FAMILY` explicitly or
  leave `auto` to detect from `MODEL_NAME`
- OpenAI-style error responses (`{"error": {"message", "type", "param", "code"}}`)

`stream=true` and multi-model support raise a 400 for now — they land in
Phase 2.
