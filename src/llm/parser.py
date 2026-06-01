"""Parse and normalize LLM JSON responses for recommendation output."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any


class LLMParseError(ValueError):
    """Raised when response cannot be parsed as expected JSON payload."""


@dataclass(frozen=True)
class ParsedRecommendation:
    id: str
    rank: int
    explanation: str
    preference_matches: list[str]


@dataclass(frozen=True)
class ParsedLLMResponse:
    summary: str | None
    recommendations: list[ParsedRecommendation]


_JSON_BLOCK_RE = re.compile(r"\{[\s\S]*\}")


def _extract_json_text(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
        text = text.strip()

    if text.startswith("{") and text.endswith("}"):
        return text

    match = _JSON_BLOCK_RE.search(text)
    if match:
        return match.group(0)
    raise LLMParseError("No JSON object found in LLM response.")


def _to_recommendation(item: dict[str, Any], fallback_rank: int) -> ParsedRecommendation:
    rid = str(item.get("id") or item.get("restaurant_id") or "").strip()
    if not rid:
        raise LLMParseError("Recommendation item missing 'id'.")

    rank = item.get("rank", fallback_rank)
    try:
        rank_int = int(rank)
    except (TypeError, ValueError) as exc:
        raise LLMParseError(f"Invalid rank for recommendation id={rid!r}.") from exc

    explanation = str(item.get("explanation") or "").strip()
    if not explanation:
        explanation = "Matches your preferences based on location, budget, and rating."

    matches_raw = item.get("preference_matches") or []
    if isinstance(matches_raw, list):
        matches = [str(x) for x in matches_raw if str(x).strip()]
    else:
        matches = []

    return ParsedRecommendation(
        id=rid,
        rank=rank_int,
        explanation=explanation,
        preference_matches=matches,
    )


def parse_llm_response(raw_text: str) -> ParsedLLMResponse:
    """Parse raw LLM output into normalized structured response."""
    json_text = _extract_json_text(raw_text)
    try:
        payload = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise LLMParseError(f"Invalid JSON from LLM: {exc}") from exc

    summary_raw = payload.get("summary")
    summary = str(summary_raw).strip() if isinstance(summary_raw, str) and summary_raw.strip() else None

    recs_raw = payload.get("recommendations")
    if not isinstance(recs_raw, list):
        raise LLMParseError("Missing or invalid 'recommendations' array.")

    recs = [_to_recommendation(item, i + 1) for i, item in enumerate(recs_raw) if isinstance(item, dict)]
    if not recs:
        raise LLMParseError("No recommendation objects parsed from response.")

    return ParsedLLMResponse(summary=summary, recommendations=recs)
