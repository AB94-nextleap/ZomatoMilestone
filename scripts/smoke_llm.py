#!/usr/bin/env python
"""Phase 4 smoke test for Groq adapter + recommendation engine."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.filters import build_candidates
from src.llm import GroqLLMAdapter, run_recommendation_engine
from src.store import RestaurantStore
from src.validation import PreferencesValidator


def main() -> int:
    store = RestaurantStore.load()
    validator = PreferencesValidator(store)
    prefs = validator.validate(
        {
            "location": "Bangalore",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )
    filtered = build_candidates(prefs, store)
    if not filtered.candidates:
        print("No candidates found for smoke test:", filtered.suggestions)
        return 1

    adapter = GroqLLMAdapter()
    response = run_recommendation_engine(
        prefs=prefs,
        candidates=filtered.candidates[:10],
        adapter=adapter,
        top_k=5,
    )
    print("Summary:", response.summary)
    for rec in response.recommendations:
        print(f"- #{rec.rank} {rec.restaurant.name}: {rec.explanation}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
