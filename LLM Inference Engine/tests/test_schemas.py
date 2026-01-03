from app.schemas import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    CompletionRequest,
    CompletionResponse,
    ErrorResponse,
    ModelList,
)


def test_chat_completion_request():
    req = ChatCompletionRequest(
        model="llama-3",
        messages=[ChatMessage(role="user", content="hello")],
    )
    assert req.model == "llama-3"
    assert len(req.messages) == 1
    assert req.stream is False


def test_chat_completion_response():
    resp = ChatCompletionResponse(
        model="llama-3",
        choices=[],
        usage={"prompt_tokens": 5, "completion_tokens": 10, "total_tokens": 15},
    )
    assert resp.model == "llama-3"
    assert resp.object == "chat.completion"


def test_completion_request():
    req = CompletionRequest(
        model="qwen",
        prompt="The capital of France is",
    )
    assert req.prompt == "The capital of France is"
    assert req.max_tokens == 512


def test_completion_response():
    resp = CompletionResponse(
        model="qwen",
        choices=[{"index": 0, "text": " Paris", "finish_reason": "stop"}],
        usage={"prompt_tokens": 5, "completion_tokens": 1, "total_tokens": 6},
    )
    assert resp.object == "text_completion"


def test_model_list():
    ml = ModelList(
        data=[{"id": "test-model", "loaded": True}]
    )
    assert len(ml.data) == 1
    assert ml.data[0]["loaded"] is True


def test_error_response():
    err = ErrorResponse(
        error={"message": "test error", "type": "invalid_request_error"}
    )
    assert err.error["type"] == "invalid_request_error"
