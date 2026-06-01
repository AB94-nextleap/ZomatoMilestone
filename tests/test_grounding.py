"""Phase 4 grounding and engine tests."""

from __future__ import annotations

from src.llm.engine import ground_recommendations, run_recommendation_engine
from src.llm.parser import ParsedLLMResponse, ParsedRecommendation
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant


class _FakeAdapter:
    def __init__(self, response: str) -> None:
        self.response = response

    def complete(self, messages: list[dict[str, str]]) -> str:  # noqa: ARG002
        return self.response


def _candidate(rid: str, name: str, rating: float) -> Restaurant:
    return Restaurant(
        id=rid,
        name=name,
        location="Bangalore",
        cuisines=["Italian"],
        rating=rating,
        estimated_cost_for_two=800.0,
        budget_band="medium",
        attributes={"city": "Bangalore"},
    )


def test_grounding_drops_hallucinated_ids():
    candidates = [_candidate("r1", "A", 4.2), _candidate("r2", "B", 4.1)]
    parsed = ParsedLLMResponse(
        summary="x",
        recommendations=[
            ParsedRecommendation(id="r9", rank=1, explanation="bad", preference_matches=[]),
            ParsedRecommendation(id="r1", rank=2, explanation="good", preference_matches=["budget"]),
        ],
    )
    result = ground_recommendations(parsed, candidates, top_k=5)
    assert len(result.grounded) == 1
    assert result.grounded[0][0].id == "r1"
    assert result.dropped_ids == ["r9"]


def test_engine_fallback_when_parser_fails():
    prefs = UserPreferences(location="Bangalore", budget="medium", cuisine="Italian", min_rating=4.0)
    candidates = [_candidate("r1", "A", 4.7), _candidate("r2", "B", 4.2)]
    adapter = _FakeAdapter("not-json")
    response = run_recommendation_engine(prefs=prefs, candidates=candidates, adapter=adapter, top_k=2)
    assert len(response.recommendations) == 2
    assert "fallback" in (response.summary or "").lower()
    assert response.recommendations[0].restaurant.id == "r1"


def test_engine_grounded_success():
    prefs = UserPreferences(location="Bangalore", budget="medium")
    candidates = [_candidate("r1", "A", 4.1), _candidate("r2", "B", 4.0)]
    adapter = _FakeAdapter(
        """
        {
          "summary":"Top options",
          "recommendations":[
            {"id":"r2","rank":1,"explanation":"fits budget","preference_matches":["budget"]},
            {"id":"ghost","rank":2,"explanation":"invalid"}
          ]
        }
        """
    )
    response = run_recommendation_engine(prefs=prefs, candidates=candidates, adapter=adapter, top_k=5)
    assert (response.summary or "").startswith("Top")
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant.id == "r2"
