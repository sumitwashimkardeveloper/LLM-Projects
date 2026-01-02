from typing import Iterator, List, Optional

from llama_cpp import Llama

from .errors import ContextLengthExceededError


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
        self._model = Llama(
            model_path=model_path,
            n_ctx=n_ctx,
            n_gpu_layers=n_gpu_layers,
            n_threads=n_threads,
            verbose=verbose,
        )

    def tokenize(self, text: str) -> List[int]:
        return self._model.tokenize(text.encode("utf-8"))

    def detokenize(self, tokens: List[int]) -> str:
        return self._model.detokenize(tokens).decode("utf-8", errors="ignore")

    def is_eos(self, token_id: int) -> bool:
        return token_id == self._model.token_eos()

    def check_prompt_length(self, prompt: str) -> List[int]:
        tokens = self.tokenize(prompt)
        if len(tokens) >= self.n_ctx:
            raise ContextLengthExceededError(
                f"Prompt has {len(tokens)} tokens, which exceeds the "
                f"context window of {self.n_ctx} tokens.",
                param="messages",
            )
        return tokens

    def raw_generate(
        self,
        prompt_tokens: List[int],
        *,
        temp: float = 0.8,
        top_p: float = 0.95,
    ) -> Iterator[int]:
        return self._model.generate(prompt_tokens, top_k=40, top_p=top_p, temp=temp)
