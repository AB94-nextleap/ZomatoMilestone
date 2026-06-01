"""Canonical restaurant entity (architecture §5.1)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

BudgetBand = Literal["low", "medium", "high", "unknown"]


class Restaurant(BaseModel):
    id: str
    name: str
    location: str
    cuisines: list[str] = Field(default_factory=list)
    rating: float
    estimated_cost_for_two: float | None = None
    budget_band: BudgetBand = "unknown"
    attributes: dict[str, Any] = Field(default_factory=dict)

    model_config = {"frozen": True}
