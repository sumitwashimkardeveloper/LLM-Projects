from typing import Optional


class InferenceEngineError(Exception):
    """Base class for errors that should be surfaced as OpenAI-style JSON."""

    status_code = 500
    error_type = "internal_error"

    def __init__(self, message: str, *, param: Optional[str] = None, code: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.param = param
        self.code = code


class ModelNotLoadedError(InferenceEngineError):
    status_code = 503
    error_type = "model_not_loaded"


class ContextLengthExceededError(InferenceEngineError):
    status_code = 400
    error_type = "context_length_exceeded"


class InvalidRequestError(InferenceEngineError):
    status_code = 400
    error_type = "invalid_request_error"
