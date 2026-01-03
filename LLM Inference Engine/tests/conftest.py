import json
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


class StubEngine:
    def __init__(self):
        self.n_ctx = 4096

    def tokenize(self, text: str):
        return list(range(len(text.split())))

    def detokenize(self, tokens):
        return " ".join(str(t) for t in tokens)

    def is_eos(self, token_id: int) -> bool:
        return token_id == 2

    def check_prompt_length(self, prompt: str):
        return self.tokenize(prompt)

    def raw_generate(self, prompt_tokens, *, temp=0.8, top_p=0.95):
        words = ["Hello", "world", "test", "response"]
        for token_id in range(len(words)):
            yield token_id


@pytest.fixture
def temp_models_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        models_path = Path(tmpdir) / "models.json"
        models_path.write_text(
            json.dumps({
                "models": [
                    {"name": "test-model-1", "path": "models/test1.gguf", "family": "llama3"},
                    {"name": "test-model-2", "path": "models/test2.gguf", "family": "qwen"},
                ]
            })
        )
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        yield tmpdir
        os.chdir(old_cwd)


@pytest.fixture
def client(monkeypatch, temp_models_json):
    monkeypatch.setenv("MODELS_MANIFEST", "models.json")
    monkeypatch.setenv("N_PARALLEL", "1")
    monkeypatch.setenv("MAX_QUEUE_DEPTH", "32")

    from app.registry import ModelRegistry
    from app.scheduler import BatchScheduler

    original_init = BatchScheduler.__init__

    def patched_init(self, *, engine_factory, **kwargs):
        self.max_queue = kwargs.get("max_queue", 64)
        self.request_timeout = kwargs.get("request_timeout", 120.0)
        self._pending = __import__("queue").Queue()
        self._slots = [
            type("Slot", (), {
                "index": 0,
                "engine": StubEngine(),
                "job": None,
                "generator": None,
                "generated_text": "",
                "n_generated": 0,
                "busy": False,
            })()
        ]
        self._wake = __import__("threading").Event()
        self._stop = __import__("threading").Event()
        self._thread = __import__("threading").Thread(target=lambda: None, daemon=True)

    monkeypatch.setattr(BatchScheduler, "__init__", patched_init)

    return TestClient(app)


@pytest.fixture
def valid_api_key(monkeypatch):
    monkeypatch.setenv("API_KEYS", "test-key-1,test-key-2")
    return "test-key-1"
