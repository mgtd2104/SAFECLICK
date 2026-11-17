"""Reusable result components for the SafeClick UI.

These render functions keep score badges, indicator cards, and advice
consistent across pages. They only display data returned by the backend (or
the Stage 2 mock) and never compute risk themselves.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from theme import style_for


def score_card(result: dict[str, Any]) -> None:
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


def indicator_card(indicator: dict[str, Any]) -> None:
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


def recommendations_list(recommendations: list[str]) -> None:
    """Show prioritized safe-action advice as a list."""
    if not recommendations:
        st.caption("No specific actions were returned.")
        return
    for item in recommendations:
        st.markdown(f"- {item}")


def render_analysis_inline(result: dict[str, Any]) -> None:
    """Render a full analysis result inline inside a chat bubble."""
    score_card(result)

    st.markdown("**Why this score**")
    indicators = result.get("indicators") or []
    if indicators:
        for indicator in indicators:
            indicator_card(indicator)
    else:
        st.info("No individual risk indicators were detected.", icon=":material/info:")

    st.markdown("**What to do next**")
    recommendations_list(result.get("recommendations") or [])

    metadata = result.get("metadata") or {}
    st.caption(
        f"Detector: {metadata.get('detector_version', 'unknown')} · "
        f"External check used: {'yes' if metadata.get('external_check_used') else 'no'}"
    )


def result_panel(result: dict[str, Any]) -> None:
    """Render a full analysis result: score, indicators, advice, metadata.

    Kept for backward compatibility with the Learn page or other uses.
    """
    score_card(result)

    st.subheader("Why this score")
    indicators = result.get("indicators") or []
    if indicators:
        for indicator in indicators:
            indicator_card(indicator)
    else:
        st.info("No individual risk indicators were detected.", icon=":material/info:")

    st.subheader("What to do next")
    recommendations_list(result.get("recommendations") or [])

    metadata = result.get("metadata") or {}
    st.caption(
        f"Detector: {metadata.get('detector_version', 'unknown')} · "
        f"External check used: {'yes' if metadata.get('external_check_used') else 'no'}"
    )