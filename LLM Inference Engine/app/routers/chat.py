import time
import uuid
from typing import Iterator, Optional, Tuple

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from ..engine import LlamaCppEngine
from ..logging_utils import log_request
from ..registry import ModelRegistry
from ..schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Timing,
    Usage,
)
from ..streaming import SSE_DONE, format_sse
from ..templates import render_chat_prompt

router = APIRouter(tags=["chat"])


@router.post("/v1/chat/completions", response_model=None)
async def create_chat_completion(body: ChatCompletionRequest, request: Request):
    registry: ModelRegistry = request.app.state.registry
    engine = registry.get_engine(body.model)
    family = registry.get_family(body.model)

    rendered = render_chat_prompt(family, body.messages)
    stop = list(dict.fromkeys(rendered.stop + (body.stop or [])))

    request_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    if not body.stream:
        start = time.perf_counter()
        result = await run_in_threadpool(
            engine.generate,
            rendered.text,
            max_tokens=body.max_tokens,
            temperature=body.temperature,
            top_p=body.top_p,
            stop=stop,
        )
        elapsed = time.perf_counter() - start
        tokens_per_sec = result.completion_tokens / elapsed if elapsed > 0 else 0.0

        log_request(
            request_id=request_id,
            endpoint="/v1/chat/completions",
            model=body.model,
            stream=False,
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            latency_ms=elapsed * 1000,
            tokens_per_sec=tokens_per_sec,
        )

        return ChatCompletionResponse(
            id=request_id,
            created=created,
            model=body.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=result.text.strip()),
                    finish_reason=result.finish_reason,
                )
            ],
            usage=Usage(
                prompt_tokens=result.prompt_tokens,
                completion_tokens=result.completion_tokens,
                total_tokens=result.prompt_tokens + result.completion_tokens,
            ),
            timing=Timing(time_to_first_token_ms=elapsed * 1000, tokens_per_sec=tokens_per_sec),
        )

    gen: Iterator[Tuple[str, Optional[str]]] = engine.generate_stream(
        rendered.text,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        top_p=body.top_p,
        stop=stop,
    )

    start = time.perf_counter()
    # Prime the generator now, inside the route handler, so a prompt that's
    # too long for the context window raises the normal 400 error instead
    # of failing after the streaming response has already started.
    try:
        first_text, first_finish = await run_in_threadpool(next, gen)
    except StopIteration:
        first_text, first_finish = "", "stop"
    ttft = time.perf_counter() - start

    return StreamingResponse(
        _sse_chat_stream(
            gen=gen,
            first_text=first_text,
            first_finish=first_finish,
            engine=engine,
            prompt=rendered.text,
            model=body.model,
            request_id=request_id,
            created=created,
            start=start,
            ttft=ttft,
        ),
        media_type="text/event-stream",
    )


def _sse_chat_stream(
    *,
    gen: Iterator[Tuple[str, Optional[str]]],
    first_text: str,
    first_finish: Optional[str],
    engine: LlamaCppEngine,
    prompt: str,
    model: str,
    request_id: str,
    created: int,
    start: float,
    ttft: float,
) -> Iterator[str]:
    yield format_sse(
        {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {"role": "assistant"}, "finish_reason": None}],
        }
    )

    full_text = ""
    text, finish_reason = first_text, first_finish

    while True:
        if text:
            full_text += text
            yield format_sse(
                {
                    "id": request_id,
                    "object": "chat.completion.chunk",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "delta": {"content": text}, "finish_reason": None}],
                }
            )
        if finish_reason is not None:
            break
        try:
            text, finish_reason = next(gen)
        except StopIteration:
            finish_reason = "stop"
            break

    yield format_sse(
        {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [{"index": 0, "delta": {}, "finish_reason": finish_reason}],
        }
    )

    elapsed = time.perf_counter() - start
    prompt_tokens = len(engine.tokenize(prompt))
    completion_tokens = len(engine.tokenize(full_text))
    tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0.0

    yield format_sse(
        {
            "id": request_id,
            "object": "chat.completion.chunk",
            "created": created,
            "model": model,
            "choices": [],
            "usage": {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            "timing": {
                "time_to_first_token_ms": round(ttft * 1000, 1),
                "tokens_per_sec": round(tokens_per_sec, 2),
            },
        }
    )

    log_request(
        request_id=request_id,
        endpoint="/v1/chat/completions",
        model=model,
        stream=True,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=elapsed * 1000,
        ttft_ms=ttft * 1000,
        tokens_per_sec=tokens_per_sec,
    )

    yield SSE_DONE
