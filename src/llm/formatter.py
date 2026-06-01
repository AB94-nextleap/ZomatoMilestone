"""Format grounded LLM output into API/domain response models."""

from __future__ import annotations

from src.models.preferences import UserPreferences
from src.models.recommendation import Recommendation, RecommendationResponse
from src.models.restaurant import Restaurant


def format_recommendation_response(
    *,
    query: UserPreferences,
    candidate_count: int,
    ranked_items: list[tuple[Restaurant, int, str, list[str]]],
    summary: str | None = None,
    suggestions: list[str] | None = None,
) -> RecommendationResponse:
    recommendations = [
        Recommendation(
            rank=rank,
            restaurant=restaurant,
            explanation=explanation,
            highlights=highlights or None,
        )
        for restaurant, rank, explanation, highlights in ranked_items
    ]
    return RecommendationResponse(
        query=query,
        candidate_count=candidate_count,
        summary=summary,
        recommendations=recommendations,
        suggestions=suggestions,
    )
