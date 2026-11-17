"""Centralized presentation values for the SafeClick UI.

Only display data lives here (labels, colors, icons, copy). Detection and
scoring stay in the backend; the UI never computes a risk score itself.
Colors use Streamlit's predefined palette so they follow the active theme,
and every color is paired with a text label so risk never relies on color alone.
"""

APP_TITLE = "SafeClick"
APP_TAGLINE = "Explainable risk checks for suspicious messages and links."

# Per-category presentation. "color" is a Streamlit palette name for st.badge.
CATEGORY_STYLES = {
    "low": {
        "label": "Low",
        "color": "green",
        "icon": ":material/check_circle:",
        "message": (
            "Few risk signals were detected. "
            "This does not guarantee the content is safe."
        ),
    },
    "medium": {
        "label": "Medium",
        "color": "yellow",
        "icon": ":material/warning:",
        "message": (
            "Some suspicious signals were found. "
            "Verify using a trusted channel."
        ),
    },
    "high": {
        "label": "High",
        "color": "orange",
        "icon": ":material/warning:",
        "message": (
            "Several strong warning signs were found. "
            "Do not act before verifying."
        ),
    },
    "critical": {
        "label": "Critical",
        "color": "red",
        "icon": ":material/dangerous:",
        "message": (
            "A strong scam pattern was detected. "
            "Do not click, pay, install, or reply."
        ),
    },
}


def style_for(category: str) -> dict:
    """Return the presentation style for a category, defaulting to low."""
    return CATEGORY_STYLES.get(category, CATEGORY_STYLES["low"])
