import pytest
from fastapi import Request
from starlette.testclient import TestClient

from app.auth import check_api_key, get_api_key
from app.errors import AuthenticationError
from app.main import app


def test_get_api_key():
    client = TestClient(app)
    with client:
        request = Request({"type": "http", "headers": [("authorization", b"Bearer my-key")]})
        assert get_api_key(request) == "my-key"


def test_get_api_key_missing():
    client = TestClient(app)
    with client:
        request = Request({"type": "http", "headers": []})
        assert get_api_key(request) is None


def test_check_api_key_disabled(monkeypatch):
    monkeypatch.setenv("API_KEYS", "")
    from app.config import settings
    import importlib
    import app.config
    importlib.reload(app.config)

    client = TestClient(app)
    with client:
        request = Request({"type": "http", "headers": []})
        check_api_key(request)


def test_check_api_key_valid(monkeypatch):
    monkeypatch.setenv("API_KEYS", "valid-key")
    import importlib
    import app.config
    importlib.reload(app.config)

    client = TestClient(app)
    with client:
        request = Request({"type": "http", "headers": [(b"authorization", b"Bearer valid-key")]})
        check_api_key(request)


def test_check_api_key_invalid(monkeypatch):
    monkeypatch.setenv("API_KEYS", "valid-key")
    import importlib
    import app.config
    importlib.reload(app.config)

    client = TestClient(app)
    with client:
        request = Request({"type": "http", "headers": [(b"authorization", b"Bearer invalid")]})
        with pytest.raises(AuthenticationError):
            check_api_key(request)
