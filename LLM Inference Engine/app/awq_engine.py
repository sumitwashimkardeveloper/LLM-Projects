from typing import Iterator, List, Optional

from .errors import ContextLengthExceededError

try:
    import torch
    from awq import AutoAWQForCausalLM
    from transformers import AutoTokenizer
    AWQ_AVAILABLE = True
except ImportError:
    AWQ_AVAILABLE = False


class AWQEngine:
    def __init__(
        self,
        *,
        model_path: str,
        device: str = "cuda:0",
        dtype: str = "float16",
        n_ctx: int = 4096,
    ):
        if not AWQ_AVAILABLE:
            raise RuntimeError("AWQ dependencies not installed; pip install -r requirements-awq.txt")
        self.model_path = model_path
        self.device = device
        self.n_ctx = n_ctx
        self.dtype = torch.float16 if dtype == "float16" else torch.bfloat16
        self.model = AutoAWQForCausalLM.from_quantized(
            model_path, fuse_layers=True, trust_remote_code=False, device_map=device
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=False)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

    def tokenize(self, text: str) -> List[int]:
        return self.tokenizer.encode(text)

    def detokenize(self, tokens: List[int]) -> str:
        return self.tokenizer.decode(tokens, skip_special_tokens=False)

    def is_eos(self, token_id: int) -> bool:
        return token_id == self.tokenizer.eos_token_id

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
        input_ids = torch.tensor([prompt_tokens], device=self.device)
        generated = [prompt_tokens]
        for _ in range(self.n_ctx - len(prompt_tokens)):
            with torch.no_grad():
                logits = self.model(input_ids).logits
            last_logits = logits[0, -1, :] / max(temp, 1e-6)
            sorted_logits, sorted_indices = torch.sort(last_logits, descending=True)
            cumsum = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=0)
            sorted_indices_to_remove = cumsum > top_p
            sorted_indices_to_remove[0] = False
            sorted_logits[sorted_indices_to_remove] = -float("inf")
            probs = torch.softmax(sorted_logits, dim=-1)
            next_token_idx = torch.multinomial(probs, num_samples=1).item()
            next_token = sorted_indices[next_token_idx].item()
            yield next_token
            generated.append(next_token)
            input_ids = torch.tensor([generated], device=self.device)
            if next_token == self.tokenizer.eos_token_id:
                break
