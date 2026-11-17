"""Static URL analysis.

The URL is only parsed with the standard library. It is never opened, fetched,
resolved, or downloaded, and no network access happens here at all. Host
inspection uses string checks, urllib.parse, and ipaddress.
"""

from __future__ import annotations

import ipaddress
from urllib.parse import parse_qsl, urlsplit

from backend.app.rules import load_rules
from backend.app.schemas import Indicator

_URL_RULES = load_rules("url")
_INDICATORS: dict = _URL_RULES["indicators"]
_SHORTENERS = frozenset(_URL_RULES["shorteners"])
_BRANDS: dict = _URL_RULES["brands"]
_QUERY_KEYS = frozenset(_URL_RULES["suspicious_query_keys"])

# Common character substitutions used to spoof a brand name in a domain.
_HOMOGLYPHS = str.maketrans({"0": "o", "1": "l", "3": "e", "5": "s", "4": "a", "$": "s"})


def _indicator(key: str) -> Indicator:
    meta = _INDICATORS[key]
    return Indicator(
        id=key,
        title=meta["title"],
        family=meta["family"],
        evidence=meta["evidence"],
        explanation=meta["explanation"],
        contribution=meta["contribution"],
    )


def _registrable_domain(host: str) -> str:
    # shortcut: naive last-two-label split; upgrade with a public-suffix list if needed.
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def analyze_url(url: str) -> list[Indicator]:
    """Return indicators for a URL using local parsing only."""
    raw = (url or "").strip()
    if not raw:
        return []

    parts = urlsplit(raw if "://" in raw else f"//{raw}")
    host = (parts.hostname or "").lower().rstrip(".")

    found: dict[str, Indicator] = {}

    def add(key: str) -> None:
        found.setdefault(key, _indicator(key))

    if parts.scheme.lower() == "http":
        add("url.plain_http")
    if parts.username or parts.password:
        add("url.credentials")

    if host:
        try:
            ipaddress.ip_address(host)
            add("url.ip_host")
        except ValueError:
            if "xn--" in host:
                add("url.punycode")
            registrable = _registrable_domain(host)
            if registrable in _SHORTENERS:
                add("url.shortener")
            deleet = host.translate(_HOMOGLYPHS)
            if any(
                (brand in host or brand in deleet) and _registrable_domain(host) != official
                for brand, official in _BRANDS.items()
            ):
                add("url.lookalike")
            if host.count(".") >= 3:
                add("url.subdomain")

        query_keys = {key.lower() for key, _ in parse_qsl(parts.query, keep_blank_values=True)}
        if query_keys & _QUERY_KEYS:
            add("url.suspicious_query")

    return list(found.values())
