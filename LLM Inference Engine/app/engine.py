"""Thin wrapper around llama-cpp-python.

Each LlamaCppEngine owns one loaded model and one llama.cpp context. A
context can only run one generation at a time, so access is serialized
with a lock (held for the full duration of a stream, not just per-call) --
that's fine for two different models running concurrently since each has
its own engine and lock; real intra-model concurrency (continuous
batching, per-request KV cache slots) lands in Phase 3.
"""

import threading
from dataclasses import dataclass
from typing import Iterator, List, Optional, Tuple

from llama_cpp import Llama

from .errors import ContextLengthExceededError


@dataclass
class GenerationResult:
    text: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str


class LlamaCppEngine:
    def __init__(
        self,
        *,
        model_path: str,
        n_ctx: int = 4096,
        n_gpu_layers: int = 0,
        n_threads: Optional[int] = None,
        verbose: bool = False,
    ):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self._lock = threading.Lock()
        self._model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=n_threads,
            verbose=verbose,
        )

    def tokenize(self, text: str) -> List[int]:
        return self._model.tokenize(text.encode("utf-8"))

    def _check_prompt_length(self, prompt: str) -> int:
        prompt_tokens = len(self.tokenize(prompt))
        if prompt_tokens >= self.n_ctx:
            raise ContextLengthExceededError(
                f"Prompt has {prompt_tokens} tokens, which exceeds the "
                f"context window of {self.n_ctx} tokens.",
                param="messages",
            )
        return prompt_tokens

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.95,
        stop: Optional[List[str]] = None,
    ) -> GenerationResult:
        self._check_prompt_length(prompt)

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

    def generate_stream(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.8,
        top_p: float = 0.95,
        stop: Optional[List[str]] = None,
    ) -> Iterator[Tuple[str, Optional[str]]]:
        """Yields (text_delta, finish_reason) pairs; finish_reason is None
        until the final chunk. Raises before yielding anything if the
        prompt doesn't fit, so callers can prime the generator to surface
        that error before committing to a streaming response."""
        self._check_prompt_length(prompt)

        with self._lock:
            stream = self._model(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stop=stop or [],
                stream=True,
            )
            for chunk in stream:
                choice = chunk["choices"][0]
                yield choice["text"], choice.get("finish_reason")
