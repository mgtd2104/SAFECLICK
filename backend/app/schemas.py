"""Request, response, and error schemas for the SafeClick API."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.app.utils.constants import AI_MAX_ADDITION, MAX_TEXT_CHARS, MAX_URL_CHARS


class AnalyzeOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    use_ai: bool = False


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    text: str | None = Field(default=None, max_length=MAX_TEXT_CHARS)
    url: str | None = Field(default=None, max_length=MAX_URL_CHARS)
    options: AnalyzeOptions = Field(default_factory=AnalyzeOptions)

    @model_validator(mode="after")
    def require_text_or_url(self) -> "AnalyzeRequest":
        if not (self.text or "").strip() and not (self.url or "").strip():
            raise ValueError("Provide at least one of 'text' or 'url'.")
        return self


class Indicator(BaseModel):
    id: str
    title: str
    family: str
    evidence: str
    explanation: str
    contribution: int


class Metadata(BaseModel):
    detector_version: str
    external_check_used: bool = False


class AiAssessment(BaseModel):
    """Strict schema for optional AI output.

    The model may only propose a bounded amount of *extra* risk, so its output
    can raise the score but never lower it and never carry free-form content
    into the response. Unknown keys are rejected.
    """

    model_config = ConfigDict(extra="forbid")

    additional_risk: int = Field(ge=0, le=AI_MAX_ADDITION)


class AnalyzeResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    category: Literal["low", "medium", "high", "critical"]
    indicators: list[Indicator] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    metadata: Metadata


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail


def error_body(code: str, message: str) -> dict:
    """Build the single shared error payload shape."""
    return ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump()
