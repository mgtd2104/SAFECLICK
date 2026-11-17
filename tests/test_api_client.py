"""Tests for the UI's API client and the UI <-> API integration (Stage 5)."""

import io
import json
import socket
import threading
import time
import urllib.error

import pytest
import uvicorn

from backend.app.main import app
from ui import api_client

_OK_BODY = json.dumps(
    {
        "score": 62,
        "category": "high",
        "indicators": [],
        "recommendations": [],
        "metadata": {"detector_version": "stage4-rules-v1", "external_check_used": False},
    }
).encode("utf-8")


class FakeResponse:
    def __init__(self, body: bytes) -> None:
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args) -> bool:
        return False


def http_error(code: int, body: bytes) -> urllib.error.HTTPError:
    return urllib.error.HTTPError("http://test/api/analyze", code, "error", None, io.BytesIO(body))


def test_analyze_returns_parsed_response(monkeypatch):
    monkeypatch.setattr(api_client.urllib.request, "urlopen", lambda *a, **k: FakeResponse(_OK_BODY))
    result = api_client.analyze("Dear customer, verify your account", "")
    assert result["score"] == 62
    assert result["category"] == "high"


def test_request_payload_shape(monkeypatch):
    captured = {}

    def fake_urlopen(request, *args, **kwargs):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        captured["timeout"] = kwargs.get("timeout")
        return FakeResponse(_OK_BODY)

    monkeypatch.setattr(api_client.urllib.request, "urlopen", fake_urlopen)
    api_client.analyze("msg", "https://example.com", use_ai=True)

    assert captured["body"] == {
        "text": "msg",
        "url": "https://example.com",
        "options": {"use_ai": True},
    }
    assert captured["timeout"] == api_client.REQUEST_TIMEOUT_SECONDS


def test_empty_fields_are_omitted(monkeypatch):
    captured = {}

    def fake_urlopen(request, *args, **kwargs):
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(_OK_BODY)

    monkeypatch.setattr(api_client.urllib.request, "urlopen", fake_urlopen)
    api_client.analyze("", "https://example.com")
    assert set(captured["body"]) == {"url", "options"}


def test_timeout_gives_friendly_error(monkeypatch):
    def raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr(api_client.urllib.request, "urlopen", raise_timeout)
    with pytest.raises(api_client.AnalysisError) as exc:
        api_client.analyze("hi", "")
    assert "too long" in str(exc.value)


def test_connection_failure_gives_friendly_error(monkeypatch):
    def raise_url_error(*args, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(api_client.urllib.request, "urlopen", raise_url_error)
    with pytest.raises(api_client.AnalysisError) as exc:
        api_client.analyze("hi", "")
    assert "Could not reach" in str(exc.value)


def test_validation_error_surfaces_the_api_message(monkeypatch):
    body = json.dumps({"error": {"code": "validation_error", "message": "Provide at least one of 'text' or 'url'."}}).encode()

    def raise_http(*args, **kwargs):
        raise http_error(422, body)

    monkeypatch.setattr(api_client.urllib.request, "urlopen", raise_http)
    with pytest.raises(api_client.AnalysisError) as exc:
        api_client.analyze("hi", "")
    assert "Provide at least one" in str(exc.value)


def test_error_without_body_uses_status_fallback(monkeypatch):
    def raise_http(*args, **kwargs):
        raise http_error(413, b"")

    monkeypatch.setattr(api_client.urllib.request, "urlopen", raise_http)
    with pytest.raises(api_client.AnalysisError) as exc:
        api_client.analyze("hi", "")
    assert "too large" in str(exc.value)


def _free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@pytest.fixture(scope="module")
def live_api() -> str:
    """Run the real API on a local port for a true end-to-end check."""
    port = _free_port()
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(200):
        if server.started:
            break
        time.sleep(0.05)
    if not server.started:
        pytest.skip("local uvicorn server did not start")
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=5)


def test_end_to_end_analysis_over_http(live_api, monkeypatch):
    monkeypatch.setattr(api_client, "API_BASE_URL", live_api)
    result = api_client.analyze("Dear customer, your KYC is expiring. Verify your account immediately.", "")

    assert result["category"] in {"low", "medium", "high", "critical"}
    assert 0 <= result["score"] <= 100
    # The displayed score is exactly the sum of the API's indicator contributions.
    assert result["score"] == sum(i["contribution"] for i in result["indicators"])
    assert result["metadata"]["detector_version"]


def test_end_to_end_reports_backend_downtime(monkeypatch):
    monkeypatch.setattr(api_client, "API_BASE_URL", f"http://127.0.0.1:{_free_port()}")
    with pytest.raises(api_client.AnalysisError):
        api_client.analyze("hi", "")
