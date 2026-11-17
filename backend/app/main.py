"""SafeClick FastAPI application entry point.

Run with: uvicorn backend.app.main:app --reload
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.analyze import router
from backend.app.utils.errors import enforce_content_type, register_error_handlers

# Comma-separated CORS origins; defaults to the local Streamlit dev UI.
DEFAULT_ALLOWED_ORIGINS = "http://localhost:8501,http://127.0.0.1:8501"


def allowed_origins() -> list[str]:
    raw = os.environ.get("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS)
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


app = FastAPI(title="SafeClick API", version="0.1.0")

app.middleware("http")(enforce_content_type)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)
register_error_handlers(app)
app.include_router(router)
