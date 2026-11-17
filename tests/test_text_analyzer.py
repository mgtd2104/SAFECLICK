"""Tests for the text analyzer (Stage 4)."""

from backend.app.services.text_analyzer import analyze_text


def ids(indicators) -> set[str]:
    return {indicator.id for indicator in indicators}


def test_urgency_pressure_is_detected():
    indicators = analyze_text("Urgent: verify your account within 24 hours")
    assert "text.urgency" in ids(indicators)


def test_digital_arrest_family_signals_are_detected():
    text = (
        "An FIR has been filed against you. Stay on the call and do not tell anyone. "
        "Pay a verification fee to clear your name."
    )
    found = ids(analyze_text(text))
    assert {"text.case_claim", "text.stay_on_call", "text.secrecy", "text.verification_fee"} <= found
    families = {i.family for i in analyze_text(text)}
    assert "Digital arrest" in families


def test_app_lure_is_detected():
    indicators = analyze_text("Install this app now and enable unknown sources to continue")
    assert "text.app_lure" in ids(indicators)
    assert {i.family for i in indicators if i.id == "text.app_lure"} == {"App lures"}


def test_repeated_matches_of_one_rule_do_not_inflate():
    # Many urgency synonyms in one message must still yield a single indicator.
    text = "Urgent, act now, this is the final warning, your account will expire immediately"
    urgency = [i for i in analyze_text(text) if i.id == "text.urgency"]
    assert len(urgency) == 1
    assert urgency[0].contribution == 20


def test_benign_text_has_no_indicators():
    assert analyze_text("Hi, see you at lunch tomorrow at the usual place.") == []


def test_empty_text_has_no_indicators():
    assert analyze_text("") == []


def test_analysis_is_deterministic():
    text = "Your KYC is expiring, verify your account immediately"
    first = [(i.id, i.contribution) for i in analyze_text(text)]
    second = [(i.id, i.contribution) for i in analyze_text(text)]
    assert first == second
