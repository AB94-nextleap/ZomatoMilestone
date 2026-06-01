"""
Filter restaurants by user preferences and build a capped candidate list (architecture §3.4).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.config.loader import get_settings
from src.models.preferences import UserBudget, UserPreferences
from src.models.restaurant import Restaurant
from src.store.restaurant_store import RestaurantStore

_BUDGET_ORDER: tuple[UserBudget, ...] = ("low", "medium", "high")


def get_candidate_limit() -> int:
    limit = int(get_settings().get("candidate_limit", 25))
    if limit <= 0:
        raise ValueError("candidate_limit must be positive")
    return limit


def matches_location(restaurant: Restaurant, location: str) -> bool:
    """
    Match area name or parent city (e.g. Bangalore matches all areas with city=Bangalore).
    """
    target = location.strip().lower()
    if restaurant.location.lower() == target:
        return True
    city = restaurant.attributes.get("city")
    if isinstance(city, str) and city.strip().lower() == target:
        return True
    return False


def matches_rating(restaurant: Restaurant, min_rating: float | None) -> bool:
    if min_rating is None:
        return True
    return restaurant.rating >= min_rating


def matches_cuisine(restaurant: Restaurant, cuisine: str | None) -> bool:
    if not cuisine:
        return True
    needle = cuisine.strip().lower()
    if not needle:
        return True
    for item in restaurant.cuisines:
        if needle in item.lower():
            return True
    return False


def matches_budget(restaurant: Restaurant, budget: UserBudget) -> bool:
    """
    Strict budget match; restaurants with unknown band are excluded (edge-cases FLT-06).
    """
    if restaurant.budget_band == "unknown":
        return False
    return restaurant.budget_band == budget


def apply_filters(
    restaurants: list[Restaurant],
    prefs: UserPreferences,
) -> list[Restaurant]:
    """Run location → rating → cuisine → budget pipeline."""
    result: list[Restaurant] = []
    for restaurant in restaurants:
        if not matches_location(restaurant, prefs.location):
            continue
        if not matches_rating(restaurant, prefs.min_rating):
            continue
        if not matches_cuisine(restaurant, prefs.cuisine):
            continue
        if not matches_budget(restaurant, prefs.budget):
            continue
        result.append(restaurant)
    return result


def sort_candidates(restaurants: list[Restaurant]) -> list[Restaurant]:
    """Rating descending, then name ascending (FLT-04 tie-break)."""
    return sorted(restaurants, key=lambda r: (-r.rating, r.name.lower()))


@dataclass(frozen=True)
class CandidateBuildResult:
    candidates: list[Restaurant]
    suggestions: list[str]

    @property
    def is_empty(self) -> bool:
        return len(self.candidates) == 0


def generate_empty_suggestions(
    prefs: UserPreferences,
    store: RestaurantStore,
) -> list[str]:
    """Actionable hints when no restaurants match (FLT-01, task 3.7)."""
    suggestions: list[str] = []
    all_rows = store.query_all()
    base = apply_filters(all_rows, prefs)

    if base:
        return suggestions

    # Location-only matches
    loc_only = [r for r in all_rows if matches_location(r, prefs.location)]
    if not loc_only:
        cities = store.list_cities()[:8]
        suggestions.append(
            f"Try a supported location such as: {', '.join(cities)}."
        )
        return suggestions

    if prefs.cuisine:
        without_cuisine = apply_filters(
            all_rows,
            prefs.model_copy(update={"cuisine": None}),
        )
        if without_cuisine and not base:
            suggestions.append(
                f"Remove or broaden the cuisine filter (no '{prefs.cuisine}' matches in {prefs.location})."
            )

    if prefs.min_rating is not None:
        relaxed = max(0.0, prefs.min_rating - 0.5)
        with_lower_rating = apply_filters(
            all_rows,
            prefs.model_copy(update={"min_rating": relaxed}),
        )
        if with_lower_rating:
            suggestions.append(
                f"Try lowering minimum rating to {relaxed:.1f} (currently {prefs.min_rating:.1f})."
            )

    budget_only = [
        r
        for r in loc_only
        if matches_rating(r, prefs.min_rating)
        and matches_cuisine(r, prefs.cuisine)
    ]
    available_bands = {r.budget_band for r in budget_only if r.budget_band != "unknown"}
    if prefs.budget not in available_bands and available_bands:
        ordered = sorted(
            available_bands,
            key=lambda b: _BUDGET_ORDER.index(b) if b in _BUDGET_ORDER else len(_BUDGET_ORDER),
        )
        suggestions.append(
            f"Try budget '{ordered[0]}' — few restaurants in {prefs.location} match '{prefs.budget}'."
        )

    if not suggestions:
        suggestions.append(
            f"No restaurants in {prefs.location} match all filters. Try fewer constraints."
        )

    return suggestions


def build_candidates(
    prefs: UserPreferences,
    store: RestaurantStore,
    *,
    limit: int | None = None,
) -> CandidateBuildResult:
    """
    Filter, sort, and cap restaurants for the LLM integration layer.

    Does not call the LLM. Returns suggestions when the candidate list is empty.
    """
    cap = limit if limit is not None else get_candidate_limit()
    filtered = apply_filters(store.query_all(), prefs)
    sorted_rows = sort_candidates(filtered)
    candidates = sorted_rows[:cap]

    suggestions: list[str] = []
    if not candidates:
        suggestions = generate_empty_suggestions(prefs, store)

    return CandidateBuildResult(candidates=candidates, suggestions=suggestions)
