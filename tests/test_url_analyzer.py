"""Tests for the URL analyzer (Stage 4).

The analyzer must never open, fetch, follow, or download a submitted URL.
"""

import urllib.request

from backend.app.services.url_analyzer import analyze_url


def ids(url: str) -> set[str]:
    return {indicator.id for indicator in analyze_url(url)}


def test_plain_http_is_detected():
    assert "url.plain_http" in ids("http://example.com/login")


def test_shortener_is_detected():
    assert "url.shortener" in ids("https://bit.ly/3xAbCd")


def test_lookalike_domain_is_detected():
    assert "url.lookalike" in ids("https://paypal-secure-login.com/verify")


def test_homoglyph_lookalike_is_detected():
    assert "url.lookalike" in ids("https://paypa1.com/login")


def test_punycode_is_detected():
    assert "url.punycode" in ids("https://xn--pypal-4ve.com/login")


def test_embedded_credentials_are_detected():
    assert "url.credentials" in ids("http://user:secret@example.com/login")


def test_raw_ip_host_is_detected():
    assert "url.ip_host" in ids("http://192.168.0.10/login")


def test_suspicious_query_parameter_is_detected():
    assert "url.suspicious_query" in ids("https://example.com/out?redirect=https://evil.example")


def test_benign_url_has_no_indicators():
    assert analyze_url("https://www.google.com/search?q=weather") == []


def test_empty_url_has_no_indicators():
    assert analyze_url("") == []


def test_url_is_never_fetched(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError("the analyzer must not fetch submitted URLs")

    monkeypatch.setattr(urllib.request, "urlopen", fail)
    # Detection succeeds without any network access.
    assert "url.lookalike" in ids("https://paypal-secure-login.com/verify")
