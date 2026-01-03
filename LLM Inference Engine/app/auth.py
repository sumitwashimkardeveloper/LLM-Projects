from typing import Optional

from fastapi import Request

from .config import settings
from .errors import AuthenticationError


def get_api_key(request: Request) -> Optional[str]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        return auth_header[7:]
    return None


def check_api_key(request: Request) -> None:
    if not settings.api_keys:
        return
    key = get_api_key(request)
    valid_keys = set(k.strip() for k in settings.api_keys.split(",") if k.strip())
    if key not in valid_keys:
        raise AuthenticationError("Invalid or missing API key.")
