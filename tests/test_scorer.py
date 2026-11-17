"""Tests for the risk scorer (Stage 4)."""

from backend.app.schemas import Indicator
from backend.app.services.risk_scorer import category_for, evaluate


def indicator(indicator_id: str, contribution: int, family: str = "Phishing") -> Indicator:
    return Indicator(
        id=indicator_id,
        title=indicator_id,
        family=family,
        evidence="evidence",
        explanation="explanation",
        contribution=contribution,
    )


def test_score_sums_contributions():
    score, category, ordered = evaluate([indicator("a", 20), indicator("b", 18)])
    assert score == 38
    assert category == "medium"
    assert [i.id for i in ordered] == ["a", "b"]


def test_score_is_clamped_to_100():
    score, category, _ = evaluate([indicator("a", 60), indicator("b", 60)])
    assert score == 100
    assert category == "critical"


def test_empty_indicators_score_zero_low():
    score, category, ordered = evaluate([])
    assert (score, category, ordered) == (0, "low", [])


def test_duplicate_indicators_count_once():
    score, _, ordered = evaluate([indicator("a", 20), indicator("a", 20)])
    assert score == 20
    assert len(ordered) == 1


def test_indicators_are_sorted_by_contribution_desc():
    _, _, ordered = evaluate([indicator("low", 12), indicator("high", 25), indicator("mid", 20)])
    assert [i.id for i in ordered] == ["high", "mid", "low"]


def test_category_boundaries_take_the_higher_category():
    assert category_for(0) == "low"
    assert category_for(24) == "low"
    assert category_for(25) == "medium"
    assert category_for(49) == "medium"
    assert category_for(50) == "high"
    assert category_for(74) == "high"
    assert category_for(75) == "critical"
    assert category_for(100) == "critical"


def test_exact_boundary_totals_use_the_higher_category():
    assert evaluate([indicator("a", 25)])[1] == "medium"
    assert evaluate([indicator("a", 50)])[1] == "high"
    assert evaluate([indicator("a", 75)])[1] == "critical"


def test_score_is_clamped_at_both_extremes():
    assert evaluate([indicator("a", 0)])[0] == 0
    assert evaluate([indicator("a", 250)])[0] == 100
    assert evaluate([indicator("a", -50)])[0] == 0


def test_extreme_repeat_counts_once():
    score, _, ordered = evaluate([indicator("a", 90)] * 50)
    assert score == 90
    assert len(ordered) == 1
