"""API tests for the SafeClick backend skeleton (Stage 3)."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.utils.constants import MAX_REQUEST_BYTES, MAX_TEXT_CHARS, MAX_URL_CHARS
from backend.app.utils.errors import register_error_handlers

client = TestClient(app, raise_server_exceptions=False)


def assert_error(response, status_code: int) -> None:
    """Every client-facing error uses the same shape and leaks no internals."""
    assert response.status_code == status_code
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}
    assert body["error"]["message"]
    text = response.text.lower()
    for leak in ("traceback", "site-packages", "\\users\\", "/home/", 'file "'):
        assert leak not in text


def test_valid_text_returns_contract_shape():
    response = client.post("/api/analyze", json={"text": "Your KYC is expiring, verify your account now"})
    assert response.status_code == 200
    body = response.json()
    assert set(body) == {"score", "category", "indicators", "recommendations", "metadata"}
    assert 0 <= body["score"] <= 100
    assert body["category"] in {"low", "medium", "high", "critical"}
    assert isinstance(body["indicators"], list)
    assert isinstance(body["recommendations"], list)
    assert set(body["metadata"]) == {"detector_version", "external_check_used"}
    assert body["metadata"]["external_check_used"] is False


def test_url_only_request_is_valid():
    response = client.post("/api/analyze", json={"url": "http://secure-login.verify-account.example.com"})
    assert response.status_code == 200


def test_use_ai_without_configuration_stays_disabled():
    response = client.post("/api/analyze", json={"text": "hello", "options": {"use_ai": True}})
    assert response.status_code == 200
    assert response.json()["metadata"]["external_check_used"] is False


def test_empty_text_string_is_rejected():
    assert_error(client.post("/api/analyze", json={"text": ""}), 422)


def test_max_length_input_is_accepted():
    response = client.post("/api/analyze", json={"text": "a" * MAX_TEXT_CHARS})
    assert response.status_code == 200
    assert response.json()["score"] == 0


def test_text_over_the_limit_is_rejected():
    assert_error(client.post("/api/analyze", json={"text": "a" * (MAX_TEXT_CHARS + 1)}), 422)


def test_url_over_the_limit_is_rejected():
    assert_error(client.post("/api/analyze", json={"url": "a" * (MAX_URL_CHARS + 1)}), 422)


def test_missing_input_returns_422():
    assert_error(client.post("/api/analyze", json={}), 422)


def test_whitespace_only_input_returns_422():
    assert_error(client.post("/api/analyze", json={"text": "   "}), 422)


def test_unknown_field_returns_422():
    assert_error(client.post("/api/analyze", json={"text": "hi", "unexpected": 1}), 422)


def test_oversized_body_returns_413():
    response = client.post(
        "/api/analyze",
        content=b"x" * (MAX_REQUEST_BYTES + 1),
        headers={"content-type": "application/json"},
    )
    assert_error(response, 413)


def test_wrong_content_type_returns_415():
    response = client.post(
        "/api/analyze",
        content=b'{"text": "hi"}',
        headers={"content-type": "text/plain"},
    )
    assert_error(response, 415)


def test_wrong_method_returns_405():
    assert_error(client.get("/api/analyze"), 405)


def test_malformed_json_returns_422():
    response = client.post(
        "/api/analyze",
        content=b"{not json}",
        headers={"content-type": "application/json"},
    )
    assert_error(response, 422)


def test_unexpected_error_returns_generic_500():
    boom_app = FastAPI()
    register_error_handlers(boom_app)

    @boom_app.get("/boom")
    async def boom():
        raise RuntimeError("internal detail must not leak")

    boom_client = TestClient(boom_app, raise_server_exceptions=False)
    response = boom_client.get("/boom")
    assert_error(response, 500)
    assert "internal detail" not in response.text
