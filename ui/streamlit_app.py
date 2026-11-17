"""SafeClick home page: submit a suspicious message and/or URL.

Stage 5: results come from the backend API through `ui/api_client.py`. The UI
only renders the API response; it never calculates a risk score itself.
"""

from __future__ import annotations

import streamlit as st

import api_client
import components
from theme import APP_TAGLINE, APP_TITLE

st.set_page_config(
    page_title=APP_TITLE,
    page_icon=":material/security:",
    layout="centered",
)

st.title(f":material/security: {APP_TITLE}")
st.caption(APP_TAGLINE)

with st.form("analyzer"):
    st.caption(
        "Provide a suspicious message, a URL, or both. "
        "Paste links in the URL field so they can be checked."
    )
    message = st.text_area(
        "Suspicious message",
        height=150,
        max_chars=api_client.MAX_INPUT_CHARS,
        placeholder="Paste the suspicious message here.",
        key="message",
    )
    url = st.text_input(
        "Suspicious URL",
        max_chars=api_client.MAX_INPUT_CHARS,
        placeholder="https://example.com/login",
        key="url",
    )
    use_ai = st.checkbox(
        "Send this content to an external AI model for extra analysis",
        key="use_ai",
        help=(
            "Off by default, and you must tick this box each time to consent. "
            "When enabled, your message and URL are sent to the configured model "
            "provider. Rules stay the source of truth: the AI can only add risk, "
            "never remove it."
        ),
    )
    submitted = st.form_submit_button(
        "Analyze",
        icon=":material/search:",
        type="primary",
        key="analyze",
    )

st.caption(
    f"Submitted URLs are never opened or visited. "
    f"Up to {api_client.MAX_INPUT_CHARS:,} characters per field."
)

if submitted:
    text_value = message.strip()
    url_value = url.strip()
    if not text_value and not url_value:
        st.session_state.pop("result", None)
        st.warning("Enter a message, a URL, or both.", icon=":material/warning:")
    else:
        try:
            with st.spinner("Analyzing…"):
                result = api_client.analyze(text_value, url_value, use_ai=use_ai)
        except api_client.AnalysisError as error:
            st.session_state.pop("result", None)
            st.error(str(error), icon=":material/error:")
        else:
            st.session_state["result"] = result

result = st.session_state.get("result")
if result:
    st.divider()
    components.result_panel(result)
    if use_ai and not (result.get("metadata") or {}).get("external_check_used"):
        st.info(
            "AI assistance was requested but is not enabled on the server, "
            "so only the local rules were used.",
            icon=":material/info:",
        )
    if st.button("Analyze another item", icon=":material/refresh:"):
        del st.session_state["result"]
        st.rerun()

st.divider()
st.page_link("pages/Learn.py", label="Learn to spot these patterns", icon=":material/menu_book:")
