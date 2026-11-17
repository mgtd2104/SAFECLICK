"""UI behaviour tests for the Streamlit pages.

`st.testing.v1.AppTest` runs the real scripts in-process, so these tests need no
browser and no live backend. The API client is patched on the module the app
imports, keeping the checks deterministic while still exercising the real
rendering path. Covers the analyzer home page (Stage 5) and the Learn page
(Stage 7).
"""

import sys
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

UI_DIR = Path(__file__).resolve().parents[1] / "ui"
if str(UI_DIR) not in sys.path:
    sys.path.insert(0, str(UI_DIR))

import api_client  # noqa: E402  (imported after the app directory is on sys.path)

APP = str(UI_DIR / "streamlit_app.py")
LEARN_APP = str(UI_DIR / "pages" / "Learn.py")

# A response shaped exactly like the API contract (Stage 4 detector output).
API_RESULT = {
    "score": 58,
    "category": "high",
    "indicators": [
        {
            "id": "text.urgency",
            "title": "Urgency pressure",
            "family": "Phishing",
            "evidence": "The message pushes the reader to act within a short deadline.",
            "explanation": "Scammers create time pressure so people act before verifying.",
            "contribution": 20,
        }
    ],
    "recommendations": ["Do not reply or click yet."],
    "metadata": {"detector_version": "stage4-rules-v1", "external_check_used": False},
}


def markdown_text(at: AppTest) -> str:
    return "\n".join(element.value for element in at.markdown)


def test_page_renders_without_error():
    at = AppTest.from_file(APP).run()
    assert not at.exception
    assert "SafeClick" in at.title[0].value


def test_empty_chat_input_shows_no_analysis():
    """Empty chat input should not trigger analysis."""
    at = AppTest.from_file(APP).run()
    # Initial state - only welcome message
    assert not at.exception
    # Chat input is not a form, so we test by sending empty string via chat_input
    # In AppTest, chat_input can be tested by setting its value
    at.chat_input[0].set_value("").run()
    assert not at.exception
    # No analysis result should appear (no metric, no error)
    assert not at.metric
    assert not at.error


def test_successful_analysis_renders_the_api_result():
    with patch.object(api_client, "analyze", return_value=API_RESULT):
        at = AppTest.from_file(APP).run()
        # Send a message via chat input
        at.chat_input[0].set_value("Dear customer, verify your account").run()

    assert not at.exception
    # UI output matches the API response; the score is echoed, never recomputed.
    assert at.metric[0].value == "58/100"
    assert at.session_state["messages"][-1]["analysis"]["category"] == "high"
    rendered = markdown_text(at)
    assert "Urgency pressure" in rendered
    assert "Do not reply or click yet." in rendered


def test_backend_error_is_shown_without_crashing():
    def raise_error(*args, **kwargs):
        raise api_client.AnalysisError("Could not reach the analysis service.")

    with patch.object(api_client, "analyze", side_effect=raise_error):
        at = AppTest.from_file(APP).run()
        at.chat_input[0].set_value("hello").run()

    assert not at.exception
    # Error is rendered as markdown in the assistant message, not st.error()
    rendered = markdown_text(at)
    assert "Could not reach" in rendered
    assert not at.metric


def test_learn_page_renders_guides_checklists_and_disclaimers():
    at = AppTest.from_file(LEARN_APP).run()
    assert not at.exception
    assert len(at.tabs) == 5

    rendered = markdown_text(at)
    assert "Warning signs" in rendered
    assert "Do this instead" in rendered
    assert "1930" in rendered

    headings = " ".join(element.value for element in at.subheader)
    assert "Quick checklist before you act" in headings
    assert "Limitations" in headings

    # Framing: the page must never imply the tool guarantees safety.
    assert "not proof that the content is safe" in rendered


def test_clear_chat_button_resets_history():
    """Clear chat button should reset message history to welcome message."""
    with patch.object(api_client, "analyze", return_value=API_RESULT):
        at = AppTest.from_file(APP).run()
        at.chat_input[0].set_value("test message").run()
        # Verify analysis was added (welcome + user + assistant with analysis = 3)
        assert len(at.session_state["messages"]) == 3
        # Click clear chat button
        at.button[0].click().run()  # Clear chat button
        # Should reset to just welcome message
        assert len(at.session_state["messages"]) == 1
        assert at.session_state["messages"][0]["role"] == "assistant"
        assert "SafeClick" in at.session_state["messages"][0]["content"]