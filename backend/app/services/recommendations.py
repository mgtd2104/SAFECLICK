"""Recommendation selection.

Recommendations are data, not logic: a category baseline plus one action per
detected threat family, de-duplicated in a stable order.
"""

from __future__ import annotations

from backend.app.schemas import Indicator

_CATEGORY_ACTIONS = {
    "low": [
        "Treat a low score as a hint, not a guarantee that the content is safe.",
        "Verify the sender through a channel you already trust.",
    ],
    "medium": [
        "Do not reply or click yet.",
        "Contact the organisation using a number or website you look up yourself.",
    ],
    "high": [
        "Do not act on this message until you verify it independently.",
        "Open the official app or type the official address yourself instead of using the link.",
    ],
    "critical": [
        "Do not click, pay, install anything, or reply.",
        "Stop the conversation and contact a trusted person.",
        "Report fraud to your local cybercrime authority.",
    ],
}

_FAMILY_ACTIONS = {
    "Phishing": ["Never share OTPs, PINs, passwords, or card details with anyone."],
    "Digital arrest": ["No genuine agency demands payment over a message or a call."],
    "App lures": ["Do not install apps or files sent to you; use your official app store."],
    "URL": ["Do not open the link; reach the organisation through an address you type yourself."],
}


def recommendations_for(category: str, indicators: list[Indicator]) -> list[str]:
    """Return prioritized, de-duplicated guidance for the result."""
    actions = list(_CATEGORY_ACTIONS.get(category, _CATEGORY_ACTIONS["low"]))
    for family in dict.fromkeys(indicator.family for indicator in indicators):
        actions += _FAMILY_ACTIONS.get(family, [])
    return list(dict.fromkeys(actions))
