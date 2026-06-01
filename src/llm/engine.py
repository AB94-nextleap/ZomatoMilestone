"""LLM recommendation engine with parsing, grounding, and fallback logic."""

from __future__ import annotations

from dataclasses import dataclass

from src.llm.adapter import LLMAdapter
from src.llm.formatter import format_recommendation_response
from src.llm.parser import LLMParseError, ParsedLLMResponse, parse_llm_response
from src.llm.prompt import compose_messages
from src.models.preferences import UserPreferences
from src.models.recommendation import RecommendationResponse
from src.models.restaurant import Restaurant


@dataclass(frozen=True)
class GroundingResult:
    grounded: list[tuple[Restaurant, int, str, list[str]]]
    dropped_ids: list[str]


def ground_recommendations(
    parsed: ParsedLLMResponse,
    candidates: list[Restaurant],
    *,
    top_k: int,
) -> GroundingResult:
    """Keep only IDs from candidate set and merge authoritative store fields."""
    candidate_by_id = {c.id: c for c in candidates}
    grounded: list[tuple[Restaurant, int, str, list[str]]] = []
    dropped_ids: list[str] = []
    seen: set[str] = set()

    for rec in parsed.recommendations:
        if rec.id in seen:
            continue
        seen.add(rec.id)
        restaurant = candidate_by_id.get(rec.id)
        if restaurant is None:
            dropped_ids.append(rec.id)
            continue
        grounded.append((restaurant, rec.rank, rec.explanation, rec.preference_matches))
        if len(grounded) >= top_k:
            break

    return GroundingResult(grounded=grounded, dropped_ids=dropped_ids)


def rating_fallback(
    candidates: list[Restaurant],
    *,
    top_k: int,
) -> list[tuple[Restaurant, int, str, list[str]]]:
    sorted_rows = sorted(candidates, key=lambda r: (-r.rating, r.name.lower()))[:top_k]
    output: list[tuple[Restaurant, int, str, list[str]]] = []
    for idx, row in enumerate(sorted_rows, start=1):
        output.append(
            (
                row,
                idx,
                "Recommended via rating fallback because AI response was unavailable or invalid.",
                ["rating", "location", "budget"],
            )
        )
    return output


def run_recommendation_engine(
    *,
    prefs: UserPreferences,
    candidates: list[Restaurant],
    adapter: LLMAdapter,
    top_k: int = 5,
) -> RecommendationResponse:
    """
    Phase 4 engine flow:
    compose prompt -> invoke LLM -> parse JSON -> ground IDs -> fallback if needed.
    """
    messages = compose_messages(prefs, candidates, top_k=top_k)
    candidate_count = len(candidates)

    for attempt in range(1, 3):
        try:
            raw = adapter.complete(messages)
            parsed = parse_llm_response(raw)
            grounded = ground_recommendations(parsed, candidates, top_k=top_k)
            if grounded.grounded:
                return format_recommendation_response(
                    query=prefs,
                    candidate_count=candidate_count,
                    summary=parsed.summary,
                    ranked_items=grounded.grounded,
                )
        except (RuntimeError, LLMParseError, ValueError):
            if attempt == 2:
                break

    fallback = rating_fallback(candidates, top_k=top_k)
    return format_recommendation_response(
        query=prefs,
        candidate_count=candidate_count,
        summary="Used fallback ranking because the LLM response could not be safely parsed.",
        ranked_items=fallback,
    )
