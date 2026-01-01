from fastapi import APIRouter, Request

from ..config import settings
from ..errors import InvalidRequestError
from ..schemas import (
    ChatCompletionChoice,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    Usage,
)
from ..templates import detect_family, render_chat_prompt

router = APIRouter(tags=["chat"])


@router.post("/v1/chat/completions", response_model=ChatCompletionResponse)
async def create_chat_completion(body: ChatCompletionRequest, request: Request) -> ChatCompletionResponse:
    if body.stream:
        raise InvalidRequestError(
            "Streaming is not implemented yet (arrives in Phase 2). Set stream=false.",
            param="stream",
        )

    engine = request.app.state.engine

    family = settings.model_family
    if family == "auto":
        family = detect_family(settings.model_name)

    rendered = render_chat_prompt(family, body.messages)
    stop = list(dict.fromkeys(rendered.stop + (body.stop or [])))

    result = engine.generate(
        rendered.text,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        top_p=body.top_p,
        stop=stop,
    )

    return ChatCompletionResponse(
        model=settings.model_name,
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
    )
