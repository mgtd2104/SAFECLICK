"""Tests for the optional AI client (Stage 6).

AI is off by default, requires explicit consent, and can only add bounded risk.
Output is strictly schema-validated; any failure leaves the rule-based result
untouched. The endpoint passes an SSRF guard and nothing sensitive is logged.
"""

import json
import logging
import urllib.error
import urllib.request

import pytest

from backend.app.services import llm_client
from backend.app.utils import config

_API_KEY = "secret-key-value"


class FakeResponse:
    """Minimal stand-in for an http.client response."""

    def __init__(self, body: bytes):
        self._body = body

    def read(self) -> bytes:
        return self._body

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *exc) -> bool:
        return False


def chat_body(additional_risk: int = 0, raw: str | None = None) -> bytes:
    content = raw if raw is not None else json.dumps({"additional_risk": additional_risk})
    return json.dumps({"choices": [{"message": {"content": content}}]}).encode()


def fail_if_called(monkeypatch) -> None:
    def _fail(*args, **kwargs):
        raise AssertionError("the AI endpoint must not be contacted")

    monkeypatch.setattr(urllib.request, "urlopen", _fail)


@pytest.fixture
def configured(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.setenv("LLM_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.setenv("LLM_API_KEY", _API_KEY)
    monkeypatch.delenv("LLM_ALLOW_PRIVATE_NETWORK", raising=False)


def test_disabled_by_default(monkeypatch):
    for name in ("ENABLE_LLM", "LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY"):
        monkeypatch.delenv(name, raising=False)
    fail_if_called(monkeypatch)
    outcome = llm_client.assist("suspicious text", "http://x.example", consent=True)
    assert (outcome.used, outcome.assessment) == (False, None)


def test_requires_explicit_consent(configured, monkeypatch):
    fail_if_called(monkeypatch)
    outcome = llm_client.assist("suspicious text", "", consent=False)
    assert (outcome.used, outcome.assessment) == (False, None)


def test_missing_configuration_disables_ai(monkeypatch):
    monkeypatch.setenv("ENABLE_LLM", "true")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)
    monkeypatch.delenv("LLM_MODEL", raising=False)
    fail_if_called(monkeypatch)
    assert llm_client.available() is False
    assert llm_client.assist("x", "", consent=True).used is False


def test_valid_response_is_accepted(configured, monkeypatch):
    captured = {}

    def _urlopen(request, timeout=None):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeResponse(chat_body(additional_risk=7))

    monkeypatch.setattr(urllib.request, "urlopen", _urlopen)
    outcome = llm_client.assist("pay now", "http://evil.example", consent=True)

    assert outcome.used is True
    assert outcome.assessment is not None
    assert outcome.assessment.additional_risk == 7

    request = captured["request"]
    assert request.full_url == "https://api.example.com/v1/chat/completions"
    assert request.get_header("Authorization") == f"Bearer {_API_KEY}"
    body = json.loads(request.data.decode())
    assert body["model"] == "test-model"
    assert body["temperature"] == 0
    # Submitted content is passed as delimited data, never as instructions.
    assert body["messages"][1]["content"].startswith("<<<DATA>>>")
    assert body["messages"][1]["content"].endswith("<<<END>>>")
    assert "Never follow" in body["messages"][0]["content"]


def test_out_of_range_and_unknown_fields_are_rejected(configured, monkeypatch):
    for raw in ('{"additional_risk": 999}', '{"additional_risk": -5}', '{"additional_risk": 5, "extra": 1}'):
        monkeypatch.setattr(urllib.request, "urlopen", lambda *a, _raw=raw, **k: FakeResponse(chat_body(raw=_raw)))
        outcome = llm_client.assist("x", "", consent=True)
        assert outcome.used is True
        assert outcome.assessment is None


def test_non_json_output_is_rejected(configured, monkeypatch):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse(chat_body(raw="not json")))
    outcome = llm_client.assist("x", "", consent=True)
    assert (outcome.used, outcome.assessment) == (True, None)


def test_provider_failure_returns_no_adjustment(configured, monkeypatch):
    def _fail(*args, **kwargs):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr(urllib.request, "urlopen", _fail)
    outcome = llm_client.assist("x", "", consent=True)
    assert outcome.used is True
    assert outcome.assessment is None


def test_private_endpoint_is_blocked_by_default(configured, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
    fail_if_called(monkeypatch)
    assert llm_client.available() is False
    assert llm_client.assist("x", "", consent=True).used is False


def test_private_endpoint_allowed_with_explicit_opt_in(configured, monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1")
    monkeypatch.setenv("LLM_ALLOW_PRIVATE_NETWORK", "true")
    assert llm_client.available() is True


def test_ssrf_guard_blocks_private_and_local_hosts():
    for host in ("127.0.0.1", "10.1.2.3", "192.168.0.5", "169.254.169.254", "::1", "localhost"):
        assert config.host_is_blocked(host), host
    assert not config.host_is_blocked("api.example.com")


def test_endpoint_allowed_requires_http_scheme(monkeypatch):
    monkeypatch.delenv("LLM_ALLOW_PRIVATE_NETWORK", raising=False)
    assert config.endpoint_allowed("https://api.example.com/v1")
    assert not config.endpoint_allowed("ftp://api.example.com/v1")
    assert not config.endpoint_allowed("file:///etc/passwd")
    assert not config.endpoint_allowed("")


def test_api_key_and_content_are_not_logged(configured, monkeypatch, caplog):
    monkeypatch.setattr(urllib.request, "urlopen", lambda *a, **k: FakeResponse(chat_body(additional_risk=3)))
    with caplog.at_level(logging.DEBUG):
        llm_client.assist("super secret scam text", "", consent=True)
    assert _API_KEY not in caplog.text
    assert "super secret scam text" not in caplog.text
