from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings
from .errors import InferenceEngineError
from .registry import ModelRegistry
from .routers import chat, completions, models
from .schemas import ErrorDetail, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.registry = ModelRegistry(settings)
    yield
    app.state.registry.shutdown_all()


app = FastAPI(title="LLM Inference Engine", version="0.3.0", lifespan=lifespan)


@app.exception_handler(InferenceEngineError)
async def handle_inference_error(request: Request, exc: InferenceEngineError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=ErrorDetail(
                message=exc.message,
                type=exc.error_type,
                param=exc.param,
                code=exc.code,
            )
        ).model_dump(),
    )


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


app.include_router(chat.router)
app.include_router(completions.router)
app.include_router(models.router)
