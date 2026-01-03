import threading
import time
from typing import Dict

from .config import settings
from .errors import RateLimitedError


class RateLimiter:
    def __init__(self, rpm: int = 0):
        self.rpm = rpm
        self.window_s = 60
        self._lock = threading.Lock()
        self._buckets: Dict[str, list] = {}

    def check(self, key: str) -> None:
        if self.rpm <= 0:
            return
        with self._lock:
            now = time.time()
            if key not in self._buckets:
                self._buckets[key] = []
            bucket = self._buckets[key]
            bucket[:] = [t for t in bucket if now - t < self.window_s]
            if len(bucket) >= self.rpm:
                raise RateLimitedError(
                    f"Rate limit of {self.rpm} requests/minute exceeded for key {key}."
                )
            bucket.append(now)


_limiter = RateLimiter(settings.rate_limit_rpm)


def check_rate_limit(key: str) -> None:
    _limiter.check(key)
