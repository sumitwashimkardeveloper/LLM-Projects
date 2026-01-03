import time
import uuid
from typing import Iterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from ..auth import check_api_key
from ..errors import ContextLengthExceededError, RequestTimeoutError
from ..logging_utils import log_request
from ..metrics import metrics
from ..rate_limit import check_rate_limit
from ..registry import ModelRegistry
from ..scheduler import BatchScheduler, GenerationJob
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


def _drain(job: GenerationJob):
    full_text = ""
    finish_reason = "stop"
    first_token_time = None
    while True:
        item = job.out_queue.get()
        if item is None:
            break
        text, reason = item
        if text:
            if first_token_time is None:
                first_token_time = time.perf_counter()
            full_text += text
        if reason is not None:
            finish_reason = reason
    return full_text, finish_reason, first_token_time


@router.post("/v1/chat/completions", response_model=None)
async def create_chat_completion(body: ChatCompletionRequest, request: Request):
    check_api_key(request)
    check_rate_limit(request.client.host if request.client else "unknown")
    metrics.record_request("/v1/chat/completions")

    registry: ModelRegistry = request.app.state.registry
    scheduler = registry.get_scheduler(body.model)
    family = registry.get_family(body.model)

    rendered = render_chat_prompt(family, body.messages)
    stop = list(dict.fromkeys(rendered.stop + (body.stop or [])))

    request_id = f"chatcmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    job = GenerationJob(
        prompt=rendered.text,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        top_p=body.top_p,
        stop=stop,
    )
    start = time.perf_counter()
    scheduler.submit(job)

    if not body.stream:
        full_text, finish_reason, first_token_time = await run_in_threadpool(_drain, job)
        elapsed = time.perf_counter() - start

        if finish_reason == "context_length_exceeded":
            raise ContextLengthExceededError(
                "Prompt exceeds the model's context window.", param="messages"
            )
        if finish_reason == "timeout":
            raise RequestTimeoutError("Request timed out while queued.")
        if finish_reason not in ("stop", "length"):
            finish_reason = "stop"

        prompt_tokens = len(scheduler.tokenize(rendered.text))
        completion_tokens = len(scheduler.tokenize(full_text))
        tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0.0

        log_request(
            request_id=request_id,
            endpoint="/v1/chat/completions",
            model=body.model,
            stream=False,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=elapsed * 1000,
            tokens_per_sec=tokens_per_sec,
        )
        metrics.record_latency("/v1/chat/completions", elapsed * 1000)
        metrics.record_tokens("/v1/chat/completions", completion_tokens, tokens_per_sec)

        return ChatCompletionResponse(
            id=request_id,
            created=created,
            model=body.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatMessage(role="assistant", content=full_text.strip()),
                    finish_reason=finish_reason,
                )
            ],
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens,
            ),
            timing=Timing(time_to_first_token_ms=elapsed * 1000, tokens_per_sec=tokens_per_sec),
        )

    first_text, first_finish = await run_in_threadpool(job.out_queue.get)
    if first_finish == "context_length_exceeded":
        raise ContextLengthExceededError(
            "Prompt exceeds the model's context window.", param="messages"
        )
    if first_finish == "timeout":
        raise RequestTimeoutError("Request timed out while queued.")

    return StreamingResponse(
        _sse_chat_stream(
            job=job,
            first_text=first_text,
            first_finish=first_finish,
            scheduler=scheduler,
            prompt=rendered.text,
            model=body.model,
            request_id=request_id,
            created=created,
            start=start,
        ),
        media_type="text/event-stream",
    )


def _sse_chat_stream(
    *,
    job: GenerationJob,
    first_text: str,
    first_finish,
    scheduler: BatchScheduler,
    prompt: str,
    model: str,
    request_id: str,
    created: int,
    start: float,
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

    try:
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
            item = job.out_queue.get()
            if item is None:
                finish_reason = "stop"
                break
            text, finish_reason = item
    finally:
        job.cancel_event.set()

    if finish_reason not in ("stop", "length"):
        finish_reason = "stop"

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
    prompt_tokens = len(scheduler.tokenize(prompt))
    completion_tokens = len(scheduler.tokenize(full_text))
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
                "time_to_first_token_ms": elapsed * 1000,
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
        tokens_per_sec=tokens_per_sec,
    )
    metrics.record_latency("/v1/chat/completions", elapsed * 1000)
    metrics.record_tokens("/v1/chat/completions", completion_tokens, tokens_per_sec)

    yield SSE_DONE
