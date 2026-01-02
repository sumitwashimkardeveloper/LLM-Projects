import time
import uuid
from typing import Iterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from starlette.concurrency import run_in_threadpool

from ..errors import ContextLengthExceededError, RequestTimeoutError
from ..logging_utils import log_request
from ..registry import ModelRegistry
from ..scheduler import BatchScheduler, GenerationJob
from ..schemas import CompletionChoice, CompletionRequest, CompletionResponse, Timing, Usage
from ..streaming import SSE_DONE, format_sse

router = APIRouter(tags=["completions"])


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


@router.post("/v1/completions", response_model=None)
async def create_completion(body: CompletionRequest, request: Request):
    registry: ModelRegistry = request.app.state.registry
    scheduler = registry.get_scheduler(body.model)

    request_id = f"cmpl-{uuid.uuid4().hex}"
    created = int(time.time())

    job = GenerationJob(
        prompt=body.prompt,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        top_p=body.top_p,
        stop=body.stop or [],
    )
    start = time.perf_counter()
    scheduler.submit(job)

    if not body.stream:
        full_text, finish_reason, first_token_time = await run_in_threadpool(_drain, job)
        elapsed = time.perf_counter() - start

        if finish_reason == "context_length_exceeded":
            raise ContextLengthExceededError(
                "Prompt exceeds the model's context window.", param="prompt"
            )
        if finish_reason == "timeout":
            raise RequestTimeoutError("Request timed out while queued.")
        if finish_reason not in ("stop", "length"):
            finish_reason = "stop"

        prompt_tokens = len(scheduler.tokenize(body.prompt))
        completion_tokens = len(scheduler.tokenize(full_text))
        tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0.0

        log_request(
            request_id=request_id,
            endpoint="/v1/completions",
            model=body.model,
            stream=False,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            latency_ms=elapsed * 1000,
            tokens_per_sec=tokens_per_sec,
        )

        return CompletionResponse(
            id=request_id,
            created=created,
            model=body.model,
            choices=[CompletionChoice(index=0, text=full_text, finish_reason=finish_reason)],
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
            "Prompt exceeds the model's context window.", param="prompt"
        )
    if first_finish == "timeout":
        raise RequestTimeoutError("Request timed out while queued.")

    return StreamingResponse(
        _sse_completion_stream(
            job=job,
            first_text=first_text,
            first_finish=first_finish,
            scheduler=scheduler,
            prompt=body.prompt,
            model=body.model,
            request_id=request_id,
            created=created,
            start=start,
        ),
        media_type="text/event-stream",
    )


def _sse_completion_stream(
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
    full_text = ""
    text, finish_reason = first_text, first_finish

    try:
        while True:
            if finish_reason not in ("stop", "length") and finish_reason is not None:
                finish_reason = "stop"
            full_text += text
            yield format_sse(
                {
                    "id": request_id,
                    "object": "text_completion",
                    "created": created,
                    "model": model,
                    "choices": [{"index": 0, "text": text, "finish_reason": finish_reason}],
                }
            )
            if finish_reason is not None:
                break
            item = job.out_queue.get()
            if item is None:
                text, finish_reason = "", "stop"
                yield format_sse(
                    {
                        "id": request_id,
                        "object": "text_completion",
                        "created": created,
                        "model": model,
                        "choices": [{"index": 0, "text": "", "finish_reason": finish_reason}],
                    }
                )
                break
            text, finish_reason = item
    finally:
        job.cancel_event.set()

    elapsed = time.perf_counter() - start
    prompt_tokens = len(scheduler.tokenize(prompt))
    completion_tokens = len(scheduler.tokenize(full_text))
    tokens_per_sec = completion_tokens / elapsed if elapsed > 0 else 0.0

    yield format_sse(
        {
            "id": request_id,
            "object": "text_completion",
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
        endpoint="/v1/completions",
        model=model,
        stream=True,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=elapsed * 1000,
        tokens_per_sec=tokens_per_sec,
    )

    yield SSE_DONE
