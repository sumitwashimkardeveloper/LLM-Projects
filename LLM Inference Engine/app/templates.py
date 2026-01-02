"""Per-model-family chat prompt templating.

llama-cpp-python can auto-apply a chat template embedded in newer GGUF
files, but we render prompts ourselves so behavior is explicit and
consistent across models that don't carry (or carry incorrect) template
metadata.
"""

from dataclasses import dataclass
from typing import List, Literal

from .schemas import ChatMessage

ModelFamily = Literal["llama3", "mistral", "qwen", "gemma", "generic"]
ALLOWED_FAMILIES = frozenset(("llama3", "mistral", "qwen", "gemma", "generic"))


@dataclass
class RenderedPrompt:
    text: str
    stop: List[str]


def detect_family(model_name: str) -> ModelFamily:
    name = model_name.lower()
    if "llama-3" in name or "llama3" in name:
        return "llama3"
    if "mistral" in name or "mixtral" in name:
        return "mistral"
    if "qwen" in name:
        return "qwen"
    if "gemma" in name:
        return "gemma"
    return "generic"


def render_llama3(messages: List[ChatMessage]) -> RenderedPrompt:
    parts = ["<|begin_of_text|>"]
    for m in messages:
        parts.append(f"<|start_header_id|>{m.role}<|end_header_id|>\n\n{m.content}<|eot_id|>")
    parts.append("<|start_header_id|>assistant<|end_header_id|>\n\n")
    return RenderedPrompt(text="".join(parts), stop=["<|eot_id|>"])


def render_qwen(messages: List[ChatMessage]) -> RenderedPrompt:
    parts = []
    for m in messages:
        parts.append(f"<|im_start|>{m.role}\n{m.content}<|im_end|>\n")
    parts.append("<|im_start|>assistant\n")
    return RenderedPrompt(text="".join(parts), stop=["<|im_end|>"])


def render_mistral(messages: List[ChatMessage]) -> RenderedPrompt:
    # Mistral's official template has no system role; fold it into the
    # first user turn instead.
    system = "\n".join(m.content for m in messages if m.role == "system")
    turns = [m for m in messages if m.role != "system"]

    parts = ["<s>"]
    pending_system = system
    for m in turns:
        if m.role == "user":
            content = m.content
            if pending_system:
                content = f"{pending_system}\n\n{content}"
                pending_system = ""
            parts.append(f"[INST] {content} [/INST]")
        else:
            parts.append(f"{m.content}</s>")
    return RenderedPrompt(text="".join(parts), stop=["</s>"])


def render_gemma(messages: List[ChatMessage]) -> RenderedPrompt:
    # Gemma has no system role either; fold it into the first user turn.
    system = "\n".join(m.content for m in messages if m.role == "system")
    turns = [m for m in messages if m.role != "system"]

    parts = []
    pending_system = system
    for m in turns:
        role = "model" if m.role == "assistant" else "user"
        content = m.content
        if role == "user" and pending_system:
            content = f"{pending_system}\n\n{content}"
            pending_system = ""
        parts.append(f"<start_of_turn>{role}\n{content}<end_of_turn>\n")
    parts.append("<start_of_turn>model\n")
    return RenderedPrompt(text="".join(parts), stop=["<end_of_turn>"])


_RENDERERS = {
    "llama3": render_llama3,
    "qwen": render_qwen,
    "mistral": render_mistral,
    "gemma": render_gemma,
    # ChatML is a widely supported fallback for unrecognized instruct models.
    "generic": render_qwen,
}


def render_chat_prompt(family: ModelFamily, messages: List[ChatMessage]) -> RenderedPrompt:
    return _RENDERERS[family](messages)
