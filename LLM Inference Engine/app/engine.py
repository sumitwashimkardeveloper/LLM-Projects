"""Thin wrapper around llama-cpp-python.

Phase 1 serves one request at a time: a single llama.cpp context can only
run one generation at a time, so access is serialized with a lock. Real
concurrency (continuous batching, per-request KV cache slots) lands in
Phase 3.
"""

import threading
from dataclasses import dataclass
from typing import List, Optional

from llama_cpp import Llama

from .config import Settings
from .errors import ContextLengthExceededError


@dataclass
class GenerationResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


class LlamaCppEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._lock = threading.Lock()
        self._model = Llama(
            model_path=settings.model_path,
            n_ctx=settings.n_ctx,
            n_gpu_layers=settings.n_gpu_layers,
            n_threads=settings.n_threads,
            verbose=settings.verbose,
        )

    def tokenize(self, text: str) -> List[int]:
        return self._model.tokenize(text.encode("utf-8"))

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.95,
        stop: Optional[List[str]] = None,
    ) -> GenerationResult:
        prompt_tokens = len(self.tokenize(prompt))
        if prompt_tokens >= self.settings.n_ctx:
            raise ContextLengthExceededError(
                f"Prompt has {prompt_tokens} tokens, which exceeds the "
                f"context window of {self.settings.n_ctx} tokens.",
                param="messages",
            )

        with self._lock:
            output = self._model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
            )

        choice = output["choices"][0]
        usage = output["usage"]
        return GenerationResult(
            text=choice["text"],
            prompt_tokens=usage["prompt_tokens"],
            completion_tokens=usage["completion_tokens"],
            finish_reason=choice.get("finish_reason") or "stop",
        )
