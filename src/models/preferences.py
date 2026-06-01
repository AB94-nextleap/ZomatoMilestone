"""User preference input model (architecture §5.2)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

UserBudget = Literal["low", "medium", "high"]


class UserPreferences(BaseModel):
    location: str
    budget: UserBudget
    cuisine: str | None = None
    min_rating: float | None = None
    additional_preferences: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}
