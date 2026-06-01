"""Phase 5 orchestration tests for RecommendationService."""

from __future__ import annotations

from typing import Any

import pytest

from src.models.restaurant import Restaurant
from src.services.recommendation_service import RecommendationService, RecommendationServiceError
from src.store.restaurant_store import RestaurantStore


class _FakeAdapter:
    def __init__(self, raw: str) -> None:
        self.raw = raw

    def complete(self, messages: list[dict[str, str]]) -> str:  # noqa: ARG002
        return self.raw


def _restaurant(
    *,
    rid: str,
    name: str,
    location: str,
    rating: float,
    cuisines: list[str],
    budget_band: str,
    city: str = "Bangalore",
) -> Restaurant:
    return Restaurant(
        id=rid,
        name=name,
        location=location,
        cuisines=cuisines,
        rating=rating,
        estimated_cost_for_two=800.0,
        budget_band=budget_band,  # type: ignore[arg-type]
        attributes={"city": city},
    )


@pytest.fixture
def sample_store() -> RestaurantStore:
    rows = [
        _restaurant(
            rid="r1",
            name="Italian Prime",
            location="Koramangala",
            rating=4.6,
            cuisines=["Italian"],
            budget_band="medium",
        ),
        _restaurant(
            rid="r2",
            name="Spice Route",
            location="Indiranagar",
            rating=4.2,
            cuisines=["North Indian"],
            budget_band="low",
        ),
    ]
    return RestaurantStore(rows)


def test_recommend_success_flow(sample_store: RestaurantStore):
    adapter_calls = {"count": 0}

    def adapter_factory() -> _FakeAdapter:
        adapter_calls["count"] += 1
        return _FakeAdapter(
            """
            {
              "summary":"Top option",
              "recommendations":[
                {"id":"r1","rank":1,"explanation":"fits preferences","preference_matches":["budget","cuisine"]}
              ]
            }
            """
        )

    service = RecommendationService(
        store=sample_store,
        adapter_factory=adapter_factory,  # type: ignore[arg-type]
        top_k=5,
    )
    response = service.recommend(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )
    assert adapter_calls["count"] == 1
    assert response.candidate_count == 1
    assert len(response.recommendations) == 1
    assert response.recommendations[0].restaurant.id == "r1"


def test_recommend_zero_candidates_skips_llm(sample_store: RestaurantStore):
    adapter_calls = {"count": 0}

    def adapter_factory() -> _FakeAdapter:
        adapter_calls["count"] += 1
        return _FakeAdapter("{}")

    service = RecommendationService(
        store=sample_store,
        adapter_factory=adapter_factory,  # type: ignore[arg-type]
    )
    response = service.recommend(
        {
            "location": "Bangalore",
            "budget": "high",
            "cuisine": "Japanese",
            "min_rating": 4.9,
        }
    )
    assert adapter_calls["count"] == 0
    assert response.candidate_count == 0
    assert response.recommendations == []
    assert response.suggestions


def test_recommend_validation_error_is_structured(sample_store: RestaurantStore):
    service = RecommendationService(
        store=sample_store,
        adapter_factory=lambda: _FakeAdapter("{}"),  # type: ignore[arg-type]
    )
    with pytest.raises(RecommendationServiceError) as exc:
        service.recommend(
            {
                "location": "Bangalore",
                "budget": "invalid-budget",
            }
        )
    body = exc.value.to_dict()
    assert body["error_code"] == "VALIDATION_ERROR"
    assert body["field"] == "budget"


def test_recommend_internal_error_is_caught(sample_store: RestaurantStore):
    def bad_adapter_factory():
        raise RuntimeError("Unexpected connection failure")

    service = RecommendationService(
        store=sample_store,
        adapter_factory=bad_adapter_factory,
    )
    with pytest.raises(RecommendationServiceError) as exc:
        service.recommend(
            {
                "location": "Bangalore",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
            }
        )
    body = exc.value.to_dict()
    assert body["error_code"] == "INTERNAL_ERROR"
    assert "Something went wrong" in body["message"]

