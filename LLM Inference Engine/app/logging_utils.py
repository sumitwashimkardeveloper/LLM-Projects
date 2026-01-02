import logging
import sys
from typing import Optional

logger = logging.getLogger("inference_engine")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(handler)


def log_request(
    *,
    request_id: str,
    endpoint: str,
    model: str,
    stream: bool,
    prompt_tokens: int,
    completion_tokens: int,
    latency_ms: float,
    tokens_per_sec: float,
    ttft_ms: Optional[float] = None,
) -> None:
    fields = {
        "request_id": request_id,
        "endpoint": endpoint,
        "model": model,
        "stream": stream,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "latency_ms": round(latency_ms, 1),
        "tokens_per_sec": round(tokens_per_sec, 2),
    }
    if ttft_ms is not None:
        fields["ttft_ms"] = round(ttft_ms, 1)
    logger.info(" ".join(f"{k}={v}" for k, v in fields.items()))
