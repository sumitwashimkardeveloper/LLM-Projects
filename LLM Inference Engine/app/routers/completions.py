from fastapi import APIRouter, Request

from ..config import settings
from ..errors import InvalidRequestError
from ..schemas import CompletionChoice, CompletionRequest, CompletionResponse, Usage

router = APIRouter(tags=["completions"])


@router.post("/v1/completions", response_model=CompletionResponse)
async def create_completion(body: CompletionRequest, request: Request) -> CompletionResponse:
    if body.stream:
        raise InvalidRequestError(
            "Streaming is not implemented yet (arrives in Phase 2). Set stream=false.",
            param="stream",
        )

    engine = request.app.state.engine

    result = engine.generate(
        body.prompt,
        max_tokens=body.max_tokens,
        temperature=body.temperature,
        top_p=body.top_p,
        stop=body.stop,
    )

    return CompletionResponse(
        model=settings.model_name,
        choices=[
            CompletionChoice(
                index=0,
                text=result.text,
                finish_reason=result.finish_reason,
            )
        ],
        usage=Usage(
            prompt_tokens=result.prompt_tokens,
            completion_tokens=result.completion_tokens,
            total_tokens=result.prompt_tokens + result.completion_tokens,
        ),
    )
