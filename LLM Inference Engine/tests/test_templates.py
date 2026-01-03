from app.schemas import ChatMessage
from app.templates import detect_family, render_chat_prompt


def test_detect_family():
    assert detect_family("llama-3-8b-instruct") == "llama3"
    assert detect_family("mistral-7b") == "mistral"
    assert detect_family("qwen2.5-7b") == "qwen"
    assert detect_family("gemma-2b") == "gemma"
    assert detect_family("unknown-model") == "generic"


def test_render_llama3():
    messages = [
        ChatMessage(role="system", content="You are helpful."),
        ChatMessage(role="user", content="Hello"),
    ]
    rendered = render_chat_prompt("llama3", messages)
    assert "<|begin_of_text|>" in rendered.text
    assert "<|start_header_id|>system<|end_header_id|>" in rendered.text
    assert "<|eot_id|>" in rendered.stop


def test_render_qwen():
    messages = [ChatMessage(role="user", content="Hi")]
    rendered = render_chat_prompt("qwen", messages)
    assert "<|im_start|>user" in rendered.text
    assert "<|im_end|>" in rendered.stop


def test_render_mistral():
    messages = [ChatMessage(role="user", content="Hello")]
    rendered = render_chat_prompt("mistral", messages)
    assert "[INST]" in rendered.text
    assert "[/INST]" in rendered.text


def test_render_gemma():
    messages = [ChatMessage(role="user", content="Hi")]
    rendered = render_chat_prompt("gemma", messages)
    assert "<start_of_turn>user" in rendered.text
    assert "<end_of_turn>" in rendered.stop
