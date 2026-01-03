def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_healthz(client):
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_readyz(client):
    resp = client.get("/readyz")
    assert resp.status_code == 200
    assert "models_configured" in resp.json()


def test_models_list(client):
    resp = client.get("/v1/models")
    assert resp.status_code == 200
    data = resp.json()
    assert data["object"] == "list"
    assert len(data["data"]) > 0


def test_chat_completions_basic(client):
    resp = client.post("/v1/chat/completions", json={
        "model": "test-model-1",
        "messages": [{"role": "user", "content": "Hello"}],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["object"] == "chat.completion"
    assert "choices" in data
    assert "usage" in data


def test_completions_basic(client):
    resp = client.post("/v1/completions", json={
        "model": "test-model-1",
        "prompt": "Hello world",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["object"] == "text_completion"
    assert "choices" in data


def test_model_not_found(client):
    resp = client.post("/v1/chat/completions", json={
        "model": "nonexistent-model",
        "messages": [{"role": "user", "content": "Hi"}],
    })
    assert resp.status_code == 404
    assert resp.json()["error"]["type"] == "model_not_found"


def test_metrics_endpoint(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "request_total" in resp.text
    assert "HELP" in resp.text
