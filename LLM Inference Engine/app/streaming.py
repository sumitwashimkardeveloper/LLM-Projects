import json
from typing import Any, Dict

SSE_DONE = "data: [DONE]\n\n"


def format_sse(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data)}\n\n"
