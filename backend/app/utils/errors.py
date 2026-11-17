"""One shared error contract for every client-facing API failure.

Every error response uses the same shape and generic message, so no stack
trace, filesystem path, or internal configuration ever reaches the client.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from backend.app.schemas import error_body
from backend.app.utils.constants import MAX_REQUEST_BYTES

logger = logging.getLogger("safeclick.api")

# Status code -> (stable machine code, generic human message).
STATUS_MESSAGES = {
    405: ("method_not_allowed", "Method not allowed."),
    413: ("payload_too_large", "Input too large."),
    415: ("unsupported_media_type", "Unsupported media type."),
    422: ("validation_error", "Missing or malformed input."),
    500: ("internal_error", "An unexpected error occurred."),
}
DEFAULT_MESSAGE = ("request_failed", "Request could not be processed.")


def error_response(status_code: int) -> JSONResponse:
    code, message = STATUS_MESSAGES.get(status_code, DEFAULT_MESSAGE)
    return JSONResponse(status_code=status_code, content=error_body(code, message))


async def enforce_content_type(request: Request, call_next):
    """Reject oversized bodies (413) and non-JSON bodies (415) before parsing."""
    if request.method == "POST" and request.url.path == "/api/analyze":
        raw_length = request.headers.get("content-length")
        length = int(raw_length) if raw_length and raw_length.isdigit() else 0
        if length > MAX_REQUEST_BYTES:
            return error_response(413)
        if length:
            media = request.headers.get("content-type", "").split(";")[0].strip().lower()
            if media != "application/json" and not media.endswith("+json"):
                return error_response(415)
    return await call_next(request)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        return error_response(exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return error_response(422)

    @app.exception_handler(Exception)
    async def _unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Log only the exception type: submitted content must not reach the logs.
        logger.error("Unhandled API error (%s)", type(exc).__name__)
        return error_response(500)
