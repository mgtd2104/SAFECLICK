"""Runtime configuration for optional integrations.

All values come from environment variables; no secret is ever hardcoded here.
Optional AI is disabled unless ENABLE_LLM is explicitly enabled, and its
endpoint is rejected when it points at a private/loopback host unless the
operator opts in for a local model.
"""

from __future__ import annotations

import ipaddress
import os
from dataclasses import dataclass
from urllib.parse import urlsplit

from backend.app.utils.constants import AI_TIMEOUT_SECONDS

_TRUTHY = frozenset({"1", "true", "yes", "on"})
_LOCAL_HOST_SUFFIXES = (".localhost", ".local", ".internal")


def _flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in _TRUTHY


def llm_enabled() -> bool:
    """Optional AI is off unless the environment explicitly enables it."""
    return _flag("ENABLE_LLM")


def allow_private_network() -> bool:
    """Opt-in for local model endpoints (Ollama/LM Studio on this machine)."""
    return _flag("LLM_ALLOW_PRIVATE_NETWORK")


@dataclass(frozen=True)
class LlmSettings:
    base_url: str
    api_key: str
    model: str
    timeout: int


def llm_settings() -> LlmSettings | None:
    """Return AI settings, or None when the integration is not configured.

    An API key is optional so keyless local models can be used.
    """
    base_url = os.environ.get("LLM_BASE_URL", "").strip().rstrip("/")
    model = os.environ.get("LLM_MODEL", "").strip()
    if not (base_url and model):
        return None
    return LlmSettings(
        base_url=base_url,
        api_key=os.environ.get("LLM_API_KEY", "").strip(),
        model=model,
        timeout=AI_TIMEOUT_SECONDS,
    )


def host_is_blocked(host: str) -> bool:
    """True for loopback/private/link-local/reserved hosts and local names.

    shortcut: public hostnames are not DNS-resolved, so a name that resolves to
    a private address is not caught here; upgrade with a resolved-address check
    if the provider URL ever becomes user-supplied rather than configured.
    """
    host = (host or "").strip().strip("[]").lower()
    if not host:
        return True
    if host == "localhost" or host.endswith(_LOCAL_HOST_SUFFIXES):
        return True
    try:
        return not ipaddress.ip_address(host).is_global
    except ValueError:
        return False


def endpoint_allowed(url: str) -> bool:
    """SSRF guard: only HTTP(S) endpoints on public hosts are allowed by default."""
    if allow_private_network():
        return True
    parts = urlsplit((url or "").strip())
    if parts.scheme.lower() not in {"http", "https"}:
        return False
    return not host_is_blocked(parts.hostname or "")
