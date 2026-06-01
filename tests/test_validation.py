"""Unit tests for preference validation (Phase 2)."""

from __future__ import annotations

import pytest

from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.store.restaurant_store import RestaurantStore
from src.validation.errors import PreferenceValidationError
from src.validation.preferences_validator import (
    PreferencesValidator,
    resolve_location,
    sanitize_additional_preferences,
    validate_budget,
    validate_min_rating,
)


def _make_store() -> RestaurantStore:
    restaurants = [
        Restaurant(
            id="1",
            name="A",
            location="Koramangala",
            cuisines=["Italian"],
            rating=4.5,
            budget_band="medium",
            attributes={"city": "Bangalore"},
        ),
        Restaurant(
            id="2",
            name="B",
            location="Indiranagar",
            cuisines=["Indian"],
            rating=4.0,
            budget_band="low",
            attributes={},
        ),
    ]
    return RestaurantStore(restaurants)


class TestValidateBudget:
    def test_valid_budgets(self):
        assert validate_budget("low") == "low"
        assert validate_budget("MEDIUM") == "medium"

    def test_invalid_budget(self):
        with pytest.raises(PreferenceValidationError) as exc:
            validate_budget("cheap")
        assert exc.value.field == "budget"
        assert "low" in exc.value.suggestions


class TestValidateMinRating:
    def test_optional(self):
        assert validate_min_rating(None) is None
        assert validate_min_rating("") is None

    def test_valid(self):
        assert validate_min_rating(4.0) == 4.0

    def test_out_of_range(self):
        with pytest.raises(PreferenceValidationError) as exc:
            validate_min_rating(99)
        assert exc.value.field == "min_rating"


class TestResolveLocation:
    def test_exact_match_case_insensitive(self):
        known = ["Koramangala", "Bangalore"]
        assert resolve_location("koramangala", known) == "Koramangala"

    def test_fuzzy_typo(self):
        known = ["Bangalore", "Koramangala"]
        assert resolve_location("Banglore", known, fuzzy_threshold=0.85) == "Bangalore"

    def test_unknown_with_suggestions(self):
        known = ["Koramangala", "Indiranagar", "Bangalore"]
        with pytest.raises(PreferenceValidationError) as exc:
            resolve_location("Tokyo", known)
        assert exc.value.field == "location"
        assert len(exc.value.suggestions) <= 10
        assert exc.value.suggestions  # non-empty sample

    def test_empty_location(self):
        with pytest.raises(PreferenceValidationError) as exc:
            resolve_location("   ", ["Bangalore"])
        assert "required" in exc.value.message.lower()


class TestSanitizeAdditionalPreferences:
    def test_dedupe_and_strip(self):
        result = sanitize_additional_preferences(
            ["Quick", "quick", "  family-friendly  "]
        )
        assert result == ["Quick", "family-friendly"]

    def test_comma_separated_string(self):
        assert sanitize_additional_preferences("a, b") == ["a", "b"]

    def test_strips_html(self):
        assert sanitize_additional_preferences(["<b>fast</b>"]) == ["fast"]


class TestPreferencesValidator:
    def test_valid_preferences(self):
        validator = PreferencesValidator(_make_store())
        prefs = validator.validate(
            {
                "location": "Koramangala",
                "budget": "medium",
                "cuisine": "Italian",
                "min_rating": 4.0,
                "additional_preferences": ["family-friendly"],
            }
        )
        assert isinstance(prefs, UserPreferences)
        assert prefs.location == "Koramangala"
        assert prefs.budget == "medium"
        assert prefs.cuisine == "Italian"
        assert prefs.min_rating == 4.0
        assert prefs.additional_preferences == ["family-friendly"]

    def test_location_via_city_name(self):
        validator = PreferencesValidator(_make_store())
        prefs = validator.validate({"location": "Bangalore", "budget": "low"})
        assert prefs.location == "Bangalore"

    def test_optional_fields_omitted(self):
        validator = PreferencesValidator(_make_store())
        prefs = validator.validate({"location": "Indiranagar", "budget": "high"})
        assert prefs.cuisine is None
        assert prefs.min_rating is None
        assert prefs.additional_preferences == []

    def test_unknown_cuisine_allowed(self):
        """VAL-08: unknown cuisine is not a validation error."""
        validator = PreferencesValidator(_make_store())
        prefs = validator.validate(
            {
                "location": "Koramangala",
                "budget": "medium",
                "cuisine": "Ethiopian",
            }
        )
        assert prefs.cuisine == "Ethiopian"

    def test_error_to_dict(self):
        validator = PreferencesValidator(_make_store())
        with pytest.raises(PreferenceValidationError) as exc:
            validator.validate({"location": "Koramangala", "budget": "invalid"})
        body = exc.value.to_dict()
        assert body["error_code"] == "VALIDATION_ERROR"
        assert body["field"] == "budget"
