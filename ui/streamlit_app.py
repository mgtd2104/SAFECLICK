"""SafeClick chat-based security assistant.

A modern chat interface where users paste suspicious messages/URLs and receive
inline analysis with risk badges, threat indicators, and actionable advice.
"""

from __future__ import annotations

import re

import streamlit as st

import api_client
from theme import APP_TAGLINE, APP_TITLE, style_for


# --- Inline rendering helpers (copied from components.py to avoid import issues) ---

def _render_score_card(result: dict) -> None:
    """Show the score, category badge, and plain-language interpretation."""
    style = style_for(result.get("category", "low"))
    score = int(result.get("score", 0))
    with st.container(border=True):
        score_col, info_col = st.columns([1, 3], vertical_alignment="center")
        score_col.metric("Risk score", f"{score}/100", border=False)
        with info_col:
            st.badge(
                f"{style['label']} risk",
                icon=style["icon"],
                color=style["color"],
            )
            st.markdown(style["message"])
            st.caption("A low score is not proof that the content is safe.")


def _render_indicator_card(indicator: dict) -> None:
    """Show one indicator: what was found, its family, and its contribution."""
    with st.container(border=True):
        st.markdown(
            f"**{indicator.get('title', 'Indicator')}** "
            f":gray-badge[{indicator.get('family', 'unknown')}] "
            f"+{indicator.get('contribution', 0)}"
        )
        if indicator.get("evidence"):
            st.markdown(indicator["evidence"])
        if indicator.get("explanation"):
            st.caption(indicator["explanation"])


def _render_recommendations_list(recommendations: list[str]) -> None:
    """Show prioritized safe-action advice as a list."""
    if not recommendations:
        st.caption("No specific actions were returned.")
        return
    for item in recommendations:
        st.markdown(f"- {item}")


def _render_analysis_inline(result: dict) -> None:
    """Render a full analysis result inline inside a chat bubble."""
    _render_score_card(result)

    st.markdown("**Why this score**")
    indicators = result.get("indicators") or []
    if indicators:
        for indicator in indicators:
            _render_indicator_card(indicator)
    else:
        st.info("No individual risk indicators were detected.", icon=":material/info:")

    st.markdown("**What to do next**")
    _render_recommendations_list(result.get("recommendations") or [])

    metadata = result.get("metadata") or {}
    st.caption(
        f"Detector: {metadata.get('detector_version', 'unknown')} · "
        f"External check used: {'yes' if metadata.get('external_check_used') else 'no'}"
    )


# --- Page config & layout ---

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":material/security:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide the default sidebar navigation (page links)
st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title(f":material/security: {APP_TITLE}")
st.caption(APP_TAGLINE)

# Initialize chat history in session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hi! I'm SafeClick, your security assistant. "
                "Paste a suspicious message, a URL, or both — "
                "and I'll analyze it for phishing, digital arrest scams, "
                "malicious app lures, and suspicious URL patterns."
            ),
        }
    ]

# Render chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "assistant" and "analysis" in msg:
            # Render analysis result inline in the assistant bubble
            _render_analysis_inline(msg["analysis"])
        else:
            st.markdown(msg["content"])

# Chat input - accepts text, URLs, or both
user_input = st.chat_input(
    placeholder="Paste a suspicious message, URL, or both here…",
    key="chat_input",
)

if user_input:
    # Append user message to history
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Extract URLs from the input
    urls = re.findall(
        r"https?://[^\s]+|www\.[^\s]+", user_input
    )
    # Use first URL found, rest treated as text
    url_value = urls[0] if urls else ""
    # Remove the URL from text for analysis (optional - backend handles both)
    text_value = user_input.strip()

    # Show user message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # Analyze with backend
    with st.chat_message("assistant"):
        with st.spinner(
            "Analyzing… (first request may take up to 60 seconds "
            "while the backend wakes up)"
        ):
            try:
                result = api_client.analyze(text_value, url_value, use_ai=False)
                # Render analysis inline
                _render_analysis_inline(result)
                # Store assistant response with analysis for history
                st.session_state.messages.append(
                    {"role": "assistant", "content": "", "analysis": result}
                )
            except api_client.AnalysisError as error:
                error_msg = f"❌ {error}"
                st.error(error_msg)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_msg}
                )

    st.rerun()

# Footer with Learn link
st.divider()
col1, col2 = st.columns([1, 1])
with col1:
    st.page_link("pages/Learn.py", label=":material/menu_book: Learn to spot these patterns", icon=":material/menu_book:")
with col2:
    if st.button("Clear chat", icon=":material/delete_sweep:", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hi! I'm SafeClick, your security assistant. "
                    "Paste a suspicious message, a URL, or both — "
                    "and I'll analyze it for phishing, digital arrest scams, "
                    "malicious app lures, and suspicious URL patterns."
                ),
            }
        ]
        st.rerun()