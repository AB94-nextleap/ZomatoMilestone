"""Recommendation response models (architecture §5.3, §8)."""

from __future__ import annotations

from pydantic import BaseModel, Field

from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant


class Recommendation(BaseModel):
    rank: int
    restaurant: Restaurant
    explanation: str
    highlights: list[str] | None = None


class RecommendationResponse(BaseModel):
    query: UserPreferences
    candidate_count: int = 0
    summary: str | None = None
    recommendations: list[Recommendation] = Field(default_factory=list)
    suggestions: list[str] | None = None
