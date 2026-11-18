"""Backend access for the SafeClick UI.

Stage 5 wires the UI to `POST /api/analyze`. All detection and scoring stay in
the backend; this module only sends the request and returns the parsed
response, using the standard library only (`urllib`, `json`).

The backend base URL is read from the environment (configuration, not a
secret); no credentials are stored or hardcoded here.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

# Environment variable takes precedence; default points to the live Render backend.
API_BASE_URL = os.environ.get("API_BASE_URL", "https://safeclick-backend-82ii.onrender.com")

# Client-side input bound, mirroring the backend per-field limit.
MAX_INPUT_CHARS = 10_000

# Increased timeout to handle Render free-tier cold start (up to ~50s spin-up).
REQUEST_TIMEOUT_SECONDS = 75

# Retry configuration for cold-start handling.
MAX_ATTEMPTS = 2
RETRY_DELAY_SECONDS = 5

# HTTP status codes that indicate the backend is still waking up.
_RETRYABLE_STATUS_CODES = {502, 503, 504}

_CONNECTION_ERROR = "Could not reach the analysis service. Check that it is running and try again."
# Updated timeout message to reflect the longer wait for cold starts.
_TIMEOUT_ERROR = (
    "The analysis service took too long to respond. "
    "The backend may be waking up from sleep (first request can take up to 60 seconds). Please try again."
)
_GENERIC_ERROR = "The analysis service returned an error. Please try again."

# Friendly fallbacks for error codes that arrive without a usable message.
_STATUS_MESSAGES = {
    405: "The analysis service rejected the request. Please try again.",
    413: "The input is too large. Shorten it and try again.",
    415: "The request format was not accepted. Please try again.",
    422: "The input could not be validated. Check the message and URL, then try again.",
}


class AnalysisError(RuntimeError):
    """Raised when the analysis service cannot be reached or returns an error."""


def _server_message(error: urllib.error.HTTPError) -> str:
    """Prefer the API's own error message; fall back to a friendly one."""
    try:
        body = json.loads(error.read().decode("utf-8"))
        message = body["error"]["message"]
        if isinstance(message, str) and 0 < len(message) <= 300:
            return message
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return _STATUS_MESSAGES.get(error.code, _GENERIC_ERROR)


def analyze(text: str, url: str, use_ai: bool = False) -> dict:
    """Request an analysis from the backend and return the response as a dict.

    Raises AnalysisError with a safe, generic message so no internal detail
    reaches the UI or the user.

    Retries once (2 attempts total) with a short delay to handle Render's
    free-tier cold start (502/503/504 or connection errors during spin-up).
    """
    payload: dict = {"options": {"use_ai": use_ai}}
    if text:
        payload["text"] = text
    if url:
        payload["url"] = url

    request = urllib.request.Request(
        f"{API_BASE_URL}/api/analyze",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    last_error: Exception | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urllib.request.urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as error:
            last_error = error
            if error.code in _RETRYABLE_STATUS_CODES and attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise AnalysisError(_server_message(error)) from error
        except TimeoutError as error:
            last_error = error
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise AnalysisError(_TIMEOUT_ERROR) from error
        except (urllib.error.URLError, OSError, ValueError) as error:
            last_error = error
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_DELAY_SECONDS)
                continue
            raise AnalysisError(_CONNECTION_ERROR) from error

    # Should not reach here, but fallback for safety.
    assert last_error is not None
    raise AnalysisError(_CONNECTION_ERROR) from last_error