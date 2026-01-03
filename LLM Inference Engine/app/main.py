from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .config import settings
from .errors import InferenceEngineError
from .metrics import metrics
from .registry import ModelRegistry
from .routers import chat, completions, metrics as metrics_router, models
from .schemas import ErrorDetail, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.registry = ModelRegistry(settings)
    yield
    app.state.registry.shutdown_all()


app = FastAPI(title="LLM Inference Engine", version="0.4.0", lifespan=lifespan)


@app.exception_handler(InferenceEngineError)
async def handle_inference_error(request: Request, exc: InferenceEngineError) -> JSONResponse:
    metrics.record_error(
        request.url.path if request.url else "unknown", exc.error_type
    )
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


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "healthy"}


@app.get("/readyz")
async def readyz(request: Request) -> dict:
    registry: ModelRegistry = request.app.state.registry
    if not registry.specs:
        return {"status": "not_ready", "reason": "no models configured"}
    return {"status": "ready", "models_configured": len(registry.specs)}


app.include_router(chat.router)
app.include_router(completions.router)
app.include_router(models.router)
app.include_router(metrics_router.router)
