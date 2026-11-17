"""Risk scoring.

Scoring is separate from detection. Overlapping signals are grouped by
indicator id so a repeated match counts once, and the total is clamped to
0-100. Boundary ties fall to the higher category.
"""

from __future__ import annotations

from backend.app.schemas import Indicator
from backend.app.utils.constants import CATEGORY_BOUNDARIES

MIN_SCORE = 0
MAX_SCORE = 100


def category_for(score: int) -> str:
    """Map a score to its category; boundary ties go to the higher category."""
    for threshold, name in CATEGORY_BOUNDARIES:
        if score >= threshold:
            return name
    return CATEGORY_BOUNDARIES[-1][1]


def evaluate(indicators: list[Indicator]) -> tuple[int, str, list[Indicator]]:
    """Return (score, category, ordered indicators) for the given indicators."""
    # Group overlapping signals: identical indicator ids collapse to one entry.
    grouped = list({indicator.id: indicator for indicator in indicators}.values())
    grouped.sort(key=lambda indicator: (-indicator.contribution, indicator.id))
    score = max(MIN_SCORE, min(MAX_SCORE, sum(indicator.contribution for indicator in grouped)))
    return score, category_for(score), grouped
