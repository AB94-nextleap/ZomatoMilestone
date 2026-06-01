"""Tests for batch preprocessing and deduplication."""

from src.ingest.preprocessor import preprocess_dataset


def test_dedup_keeps_higher_rating():
    rows = [
        {
            "name": "Cafe",
            "listed_in(city)": "BTM",
            "rate": "3.5/5",
            "cuisines": "Cafe",
            "approx_cost(for two people)": "400",
        },
        {
            "name": "Cafe",
            "listed_in(city)": "BTM",
            "rate": "4.5/5",
            "cuisines": "Cafe",
            "approx_cost(for two people)": "400",
        },
    ]
    restaurants, stats = preprocess_dataset(rows)
    assert len(restaurants) == 1
    assert restaurants[0].rating == 4.5
    assert stats["duplicates_removed"] >= 1
