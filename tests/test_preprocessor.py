"""Unit tests for ingest preprocessing (Phase 1)."""

from src.ingest.preprocessor import (
    compute_budget_band,
    make_restaurant_id,
    parse_cost,
    parse_cuisines,
    parse_rating,
    preprocess_row,
)


def test_parse_rating():
    assert parse_rating("4.1/5") == 4.1
    assert parse_rating("NEW") is None
    assert parse_rating("-") is None


def test_parse_cost():
    assert parse_cost("800") == 800.0
    assert parse_cost("300-400") == 300.0
    assert parse_cost("1,200") == 1200.0


def test_parse_cuisines():
    assert parse_cuisines("North Indian, Chinese") == ["North Indian", "Chinese"]


def test_budget_band():
    bands = {"low": {"max": 500}, "medium": {"min": 500, "max": 1500}, "high": {"min": 1500}}
    assert compute_budget_band(400, bands) == "low"
    assert compute_budget_band(800, bands) == "medium"
    assert compute_budget_band(2000, bands) == "high"


def test_preprocess_row_minimal():
    row = {
        "name": "Jalsa",
        "listed_in(city)": "Banashankari",
        "location": "Banashankari",
        "rate": "4.1/5",
        "cuisines": "North Indian, Chinese",
        "approx_cost(for two people)": "800",
        "address": "Banashankari, Bangalore",
    }
    r = preprocess_row(row)
    assert r is not None
    assert r.name == "Jalsa"
    assert r.rating == 4.1
    assert r.budget_band == "medium"
    assert "Chinese" in r.cuisines
    assert r.attributes.get("city") == "Bangalore"


def test_preprocess_row_skips_invalid():
    assert preprocess_row({"name": "", "rate": "4.0"}) is None
    assert preprocess_row({"name": "X", "listed_in(city)": "Y", "rate": "NEW"}) is None


def test_stable_id():
    id1 = make_restaurant_id("A", "B", "addr")
    id2 = make_restaurant_id("A", "B", "addr")
    assert id1 == id2
