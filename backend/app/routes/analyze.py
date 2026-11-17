"""POST /api/analyze route.

Validates the request, runs the local text and URL detectors, then scores the
indicators and selects recommendations. No submitted URL is ever opened or
fetched. Optional AI assistance runs only when it is enabled and the user
explicitly consents; it can add bounded risk but can never lower the rule-based
score.
"""

from fastapi import APIRouter

from backend.app.schemas import AnalyzeRequest, AnalyzeResponse, Indicator, Metadata
from backend.app.services import llm_client, recommendations, text_analyzer, url_analyzer
from backend.app.services.risk_scorer import MAX_SCORE, category_for, evaluate
from backend.app.utils.constants import DETECTOR_VERSION

router = APIRouter()

_AI_INDICATOR = Indicator(
    id="ai.additional_risk",
    title="AI-assessed extra risk",
    family="AI assistance",
    evidence="The optional AI model flagged additional risk signals the rules did not cover.",
    explanation="Optional AI assistance can only add risk; it can never lower the rule-based score.",
    contribution=0,
)


def analyze_payload(payload: AnalyzeRequest) -> AnalyzeResponse:
    """Run rule-based detection and scoring for one validated request."""
    indicators = []
    if (payload.text or "").strip():
        indicators += text_analyzer.analyze_text(payload.text)
    if (payload.url or "").strip():
        indicators += url_analyzer.analyze_url(payload.url)

    score, category, ordered = evaluate(indicators)

    # Optional AI: only with consent, and only ever additive (clamped to 100).
    outcome = llm_client.assist(payload.text or "", payload.url or "", consent=payload.options.use_ai)
    if outcome.assessment:
        delta = min(outcome.assessment.additional_risk, MAX_SCORE - score)
        if delta > 0:
            ordered = ordered + [_AI_INDICATOR.model_copy(update={"contribution": delta})]
            score += delta
            category = category_for(score)

    return AnalyzeResponse(
        score=score,
        category=category,
        indicators=ordered,
        recommendations=recommendations.recommendations_for(category, ordered),
        metadata=Metadata(detector_version=DETECTOR_VERSION, external_check_used=outcome.used),
    )


@router.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    return analyze_payload(payload)
