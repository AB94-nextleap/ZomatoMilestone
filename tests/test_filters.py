"""Unit tests for filter pipeline and candidate builder (Phase 3)."""

from __future__ import annotations

import pytest

from src.filters.candidate_builder import (
    apply_filters,
    build_candidates,
    get_candidate_limit,
    matches_budget,
    matches_cuisine,
    matches_location,
    matches_rating,
    sort_candidates,
)
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.store.restaurant_store import RestaurantStore


def _restaurant(
    *,
    id: str,
    name: str,
    location: str,
    cuisines: list[str],
    rating: float,
    budget_band: str = "medium",
    city: str | None = "Bangalore",
    cost: float = 800.0,
) -> Restaurant:
    attrs = {"city": city} if city else {}
    return Restaurant(
        id=id,
        name=name,
        location=location,
        cuisines=cuisines,
        rating=rating,
        estimated_cost_for_two=cost,
        budget_band=budget_band,  # type: ignore[arg-type]
        attributes=attrs,
    )


@pytest.fixture
def sample_store() -> RestaurantStore:
    restaurants = [
        _restaurant(
            id="1",
            name="Italian Place",
            location="Koramangala",
            cuisines=["Italian", "Continental"],
            rating=4.5,
            budget_band="medium",
        ),
        _restaurant(
            id="2",
            name="Budget Dhaba",
            location="Koramangala",
            cuisines=["North Indian"],
            rating=3.8,
            budget_band="low",
            cost=300,
        ),
        _restaurant(
            id="3",
            name="Fine Dining",
            location="Indiranagar",
            cuisines=["Italian"],
            rating=4.2,
            budget_band="high",
            cost=2000,
        ),
        _restaurant(
            id="4",
            name="Low Rated Italian",
            location="Koramangala",
            cuisines=["Italian"],
            rating=3.5,
            budget_band="medium",
        ),
        _restaurant(
            id="5",
            name="Unknown Budget Spot",
            location="Koramangala",
            cuisines=["Italian"],
            rating=4.8,
            budget_band="unknown",
        ),
    ]
    return RestaurantStore(restaurants)


class TestMatchesLocation:
    def test_area_match(self, sample_store: RestaurantStore):
        r = sample_store.get_by_id("1")
        assert r and matches_location(r, "Koramangala")

    def test_city_match(self, sample_store: RestaurantStore):
        r = sample_store.get_by_id("1")
        assert r and matches_location(r, "Bangalore")


class TestMatchesCuisine:
    def test_substring_token(self):
        r = _restaurant(id="x", name="X", location="A", cuisines=["North Indian"], rating=4.0)
        assert matches_cuisine(r, "Indian")
        assert not matches_cuisine(r, "Italian")


class TestMatchesBudget:
    def test_unknown_excluded(self):
        r = _restaurant(
            id="x", name="X", location="A", cuisines=[], rating=4.0, budget_band="unknown"
        )
        assert not matches_budget(r, "medium")


class TestApplyFilters:
    def test_bangalore_medium_italian_min_4(self, sample_store: RestaurantStore):
        prefs = UserPreferences(
            location="Bangalore",
            budget="medium",
            cuisine="Italian",
            min_rating=4.0,
        )
        result = apply_filters(sample_store.query_all(), prefs)
        ids = {r.id for r in result}
        assert ids == {"1"}  # only Italian Place; excludes 4 (low rating), 5 (unknown budget)

    def test_koramangala_filters(self, sample_store: RestaurantStore):
        prefs = UserPreferences(location="Koramangala", budget="low")
        result = apply_filters(sample_store.query_all(), prefs)
        assert len(result) == 1
        assert result[0].id == "2"


class TestBuildCandidates:
    def test_respects_cap(self, sample_store: RestaurantStore, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "src.filters.candidate_builder.get_candidate_limit",
            lambda: 2,
        )
        prefs = UserPreferences(location="Bangalore", budget="medium")
        result = build_candidates(prefs, sample_store)
        assert len(result.candidates) <= 2
        assert result.candidates[0].rating >= result.candidates[-1].rating

    def test_empty_with_suggestions(self, sample_store: RestaurantStore):
        prefs = UserPreferences(
            location="Koramangala",
            budget="high",
            cuisine="Italian",
            min_rating=4.9,
        )
        result = build_candidates(prefs, sample_store)
        assert result.candidates == []
        assert len(result.suggestions) >= 1
        assert any("rating" in s.lower() or "filter" in s.lower() for s in result.suggestions)

    def test_sort_tiebreak_by_name(self):
        rows = [
            _restaurant(id="a", name="Zeta", location="X", cuisines=[], rating=4.0, city=None),
            _restaurant(id="b", name="Alpha", location="X", cuisines=[], rating=4.0, city=None),
        ]
        sorted_rows = sort_candidates(rows)
        assert sorted_rows[0].name == "Alpha"


class TestGetCandidateLimit:
    def test_positive(self):
        assert get_candidate_limit() >= 1
