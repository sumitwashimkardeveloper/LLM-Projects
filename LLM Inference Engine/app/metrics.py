import threading
from dataclasses import dataclass, field
from typing import Dict

import numpy as np


@dataclass
class LatencyHistogram:
    buckets: Dict[int, int] = field(default_factory=lambda: {i * 100: 0 for i in range(1, 101)})
    sum_ms: float = 0.0
    count: int = 0

    def observe(self, ms: float) -> None:
        self.sum_ms += ms
        self.count += 1
        bucket_key = min(100 * 100, (int(ms // 100) + 1) * 100)
        if bucket_key in self.buckets:
            self.buckets[bucket_key] += 1
        else:
            self.buckets[bucket_key] = 1

    def p95(self) -> float:
        if self.count == 0:
            return 0.0
        cumsum = 0
        for bucket_ms in sorted(self.buckets.keys()):
            cumsum += self.buckets[bucket_ms]
            if cumsum >= self.count * 0.95:
                return float(bucket_ms)
        return 10000.0

    def mean(self) -> float:
        return self.sum_ms / self.count if self.count > 0 else 0.0


class Metrics:
    def __init__(self):
        self._lock = threading.Lock()
        self.request_total: Dict[str, int] = {}
        self.request_errors: Dict[str, int] = {}
        self.request_latency: Dict[str, LatencyHistogram] = {}
        self.tokens_generated: Dict[str, int] = {}
        self.tokens_per_sec: Dict[str, list] = {}
        self.queue_depth: int = 0
        self.active_slots: int = 0

    def record_request(self, endpoint: str) -> None:
        with self._lock:
            self.request_total[endpoint] = self.request_total.get(endpoint, 0) + 1

    def record_error(self, endpoint: str, error_type: str) -> None:
        with self._lock:
            key = f"{endpoint}:{error_type}"
            self.request_errors[key] = self.request_errors.get(key, 0) + 1

    def record_latency(self, endpoint: str, latency_ms: float) -> None:
        with self._lock:
            if endpoint not in self.request_latency:
                self.request_latency[endpoint] = LatencyHistogram()
            self.request_latency[endpoint].observe(latency_ms)

    def record_tokens(self, endpoint: str, tokens: int, tokens_per_sec: float) -> None:
        with self._lock:
            self.tokens_generated[endpoint] = self.tokens_generated.get(endpoint, 0) + tokens
            if endpoint not in self.tokens_per_sec:
                self.tokens_per_sec[endpoint] = []
            self.tokens_per_sec[endpoint].append(tokens_per_sec)
            if len(self.tokens_per_sec[endpoint]) > 1000:
                self.tokens_per_sec[endpoint] = self.tokens_per_sec[endpoint][-1000:]

    def get_prometheus(self) -> str:
        with self._lock:
            lines = [
                "# HELP request_total Total requests",
                "# TYPE request_total counter",
            ]
            for endpoint, count in self.request_total.items():
                lines.append(f'request_total{{endpoint="{endpoint}"}} {count}')
            lines.extend([
                "# HELP request_errors Request errors by type",
                "# TYPE request_errors counter",
            ])
            for key, count in self.request_errors.items():
                lines.append(f'request_errors{{key="{key}"}} {count}')
            lines.extend([
                "# HELP request_latency_ms Request latency milliseconds",
                "# TYPE request_latency_ms histogram",
            ])
            for endpoint, hist in self.request_latency.items():
                mean = hist.mean()
                p95 = hist.p95()
                lines.append(f'request_latency_ms{{endpoint="{endpoint}",quantile="0.95"}} {p95}')
                lines.append(f'request_latency_ms{{endpoint="{endpoint}",quantile="mean"}} {mean}')
            lines.extend([
                "# HELP tokens_generated Total tokens generated",
                "# TYPE tokens_generated counter",
            ])
            for endpoint, count in self.tokens_generated.items():
                lines.append(f'tokens_generated{{endpoint="{endpoint}"}} {count}')
            lines.extend([
                "# HELP tokens_per_sec Recent tokens per second",
                "# TYPE tokens_per_sec gauge",
            ])
            for endpoint, values in self.tokens_per_sec.items():
                if values:
                    avg_tps = np.mean(values)
                    lines.append(f'tokens_per_sec{{endpoint="{endpoint}"}} {avg_tps:.2f}')
            lines.append(f"# HELP queue_depth Current queue depth\n# TYPE queue_depth gauge\nqueue_depth {self.queue_depth}")
            lines.append(f"# HELP active_slots Current active slots\n# TYPE active_slots gauge\nactive_slots {self.active_slots}")
            return "\n".join(lines) + "\n"


metrics = Metrics()
