"""Validate and normalize user preferences against the restaurant store."""

from __future__ import annotations

import re
from difflib import SequenceMatcher, get_close_matches
from typing import Any

from src.ingest.preprocessor import normalize_location
from src.models.preferences import UserBudget, UserPreferences
from src.store.restaurant_store import RestaurantStore
from src.validation.errors import PreferenceValidationError

ALLOWED_BUDGETS: frozenset[str] = frozenset({"low", "medium", "high"})
MIN_RATING = 0.0
MAX_RATING = 5.0
MAX_ADDITIONAL_PREFS = 10
MAX_ADDITIONAL_PREF_CHARS = 500
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_HTML_TAG = re.compile(r"<[^>]+>")


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _build_location_index(known_locations: list[str]) -> dict[str, str]:
    """Map lowercase location → canonical value from store."""
    index: dict[str, str] = {}
    for loc in known_locations:
        if not loc:
            continue
        index[loc.lower()] = loc
    return index


def resolve_location(
    raw_location: str,
    known_locations: list[str],
    *,
    fuzzy_threshold: float = 0.85,
    suggestion_count: int = 10,
) -> str:
    """
    Resolve user location to a canonical value from the store.

    Raises PreferenceValidationError if no exact or fuzzy match.
    """
    cleaned = raw_location.strip()
    if not cleaned:
        raise PreferenceValidationError(
            "Location is required.",
            field="location",
        )

    normalized = normalize_location(cleaned) or cleaned
    index = _build_location_index(known_locations)

    # Exact match (case-insensitive)
    if canonical := index.get(normalized.lower()):
        return canonical

    # Fuzzy match against known locations
    best_canonical: str | None = None
    best_score = 0.0
    for loc in known_locations:
        score = _similarity(normalized, loc)
        if score > best_score:
            best_score = score
            best_canonical = loc

    if best_canonical and best_score >= fuzzy_threshold:
        return best_canonical

    # Suggest close matches (VAL-02: sample 5–10, not full dump)
    sample = get_close_matches(
        normalized.lower(),
        list(index.keys()),
        n=suggestion_count,
        cutoff=0.5,
    )
    suggestions = [index[s] for s in sample]
    if not suggestions and known_locations:
        suggestions = known_locations[:suggestion_count]

    hint = f" Did you mean: {', '.join(suggestions[:5])}?" if suggestions else ""
    raise PreferenceValidationError(
        f"Unknown location '{cleaned}'.{hint}",
        field="location",
        suggestions=suggestions,
    )


def validate_budget(raw: Any) -> UserBudget:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        raise PreferenceValidationError(
            "Budget is required. Allowed values: low, medium, high.",
            field="budget",
            suggestions=["low", "medium", "high"],
        )
    value = str(raw).strip().lower()
    if value not in ALLOWED_BUDGETS:
        raise PreferenceValidationError(
            f"Invalid budget '{raw}'. Allowed values: low, medium, high.",
            field="budget",
            suggestions=["low", "medium", "high"],
        )
    return value  # type: ignore[return-value]


def validate_min_rating(raw: Any) -> float | None:
    if raw is None or raw == "":
        return None
    try:
        rating = float(raw)
    except (TypeError, ValueError) as exc:
        raise PreferenceValidationError(
            "Minimum rating must be a number between 0 and 5.",
            field="min_rating",
        ) from exc

    if rating < MIN_RATING or rating > MAX_RATING:
        raise PreferenceValidationError(
            f"Minimum rating must be between {MIN_RATING} and {MAX_RATING}.",
            field="min_rating",
        )
    return rating


def validate_cuisine(raw: Any) -> str | None:
    if raw is None or (isinstance(raw, str) and not raw.strip()):
        return None
    cuisine = str(raw).strip()
    cuisine = _CONTROL_CHARS.sub("", cuisine)
    cuisine = _HTML_TAG.sub("", cuisine).strip()
    if not cuisine:
        return None
    if len(cuisine) > 100:
        cuisine = cuisine[:100]
    return cuisine


def sanitize_additional_preferences(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        items = [p.strip() for p in raw.split(",") if p.strip()]
    elif isinstance(raw, list):
        items = [str(p).strip() for p in raw if str(p).strip()]
    else:
        raise PreferenceValidationError(
            "Additional preferences must be a list of strings.",
            field="additional_preferences",
        )

    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = _CONTROL_CHARS.sub("", item)
        cleaned = _HTML_TAG.sub("", cleaned).strip()
        if not cleaned:
            continue
        if len(cleaned) > MAX_ADDITIONAL_PREF_CHARS:
            cleaned = cleaned[:MAX_ADDITIONAL_PREF_CHARS]
        key = cleaned.lower()
        if key in seen:
            continue
        seen.add(key)
        result.append(cleaned)
        if len(result) >= MAX_ADDITIONAL_PREFS:
            break
    return result


class PreferencesValidator:
    """Validate raw preference payloads using store-backed location resolution."""

    def __init__(
        self,
        store: RestaurantStore,
        *,
        fuzzy_threshold: float = 0.85,
        suggestion_count: int = 10,
    ) -> None:
        self._known_locations = store.list_cities()
        if not self._known_locations:
            raise ValueError("Restaurant store has no locations for validation.")
        self._fuzzy_threshold = fuzzy_threshold
        self._suggestion_count = suggestion_count

    @property
    def known_locations(self) -> list[str]:
        return list(self._known_locations)

    def validate(self, data: dict[str, Any]) -> UserPreferences:
        """Validate a preference dict and return a frozen UserPreferences instance."""
        location = resolve_location(
            str(data.get("location", "")),
            self._known_locations,
            fuzzy_threshold=self._fuzzy_threshold,
            suggestion_count=self._suggestion_count,
        )
        budget = validate_budget(data.get("budget"))
        cuisine = validate_cuisine(data.get("cuisine"))
        min_rating = validate_min_rating(data.get("min_rating"))
        additional = sanitize_additional_preferences(data.get("additional_preferences"))

        return UserPreferences(
            location=location,
            budget=budget,
            cuisine=cuisine,
            min_rating=min_rating,
            additional_preferences=additional,
        )
