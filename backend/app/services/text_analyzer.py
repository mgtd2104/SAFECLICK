"""Text detection.

Matches configured rule patterns against the submitted message text and returns
one indicator per matching rule. Detection only produces indicators; it never
decides the final score or category (see risk_scorer). The text is treated as
untrusted data and matched locally with the standard library only.
"""

from __future__ import annotations

import re

from backend.app.rules import load_rules
from backend.app.schemas import Indicator

_WHITESPACE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Lowercase and collapse whitespace so patterns match reliably."""
    return _WHITESPACE.sub(" ", text.lower()).strip()


def _compile(rule: dict) -> dict:
    return {**rule, "patterns": [re.compile(pattern) for pattern in rule["patterns"]]}


_RULES = tuple(_compile(rule) for rule in load_rules("text"))


def analyze_text(text: str) -> list[Indicator]:
    """Return one indicator per matching rule, so a rule never counts twice."""
    normalized = normalize_text(text or "")
    if not normalized:
        return []
    indicators: list[Indicator] = []
    for rule in _RULES:
        if any(pattern.search(normalized) for pattern in rule["patterns"]):
            indicators.append(
                Indicator(
                    id=rule["id"],
                    title=rule["title"],
                    family=rule["family"],
                    evidence=rule["evidence"],
                    explanation=rule["explanation"],
                    contribution=rule["contribution"],
                )
            )
    return indicators
