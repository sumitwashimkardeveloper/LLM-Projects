from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from ..metrics import metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics", response_class=PlainTextResponse)
async def get_metrics() -> str:
    return metrics.get_prometheus()
