"""Tests for RestaurantStore with fixture parquet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.store.restaurant_store import RestaurantStore

FIXTURE_PATH = Path(__file__).parent / "fixtures" / "sample_restaurants.parquet"


@pytest.fixture
def sample_parquet(tmp_path: Path) -> Path:
    path = tmp_path / "restaurants.parquet"
    df = pd.DataFrame(
        [
            {
                "id": "abc123",
                "name": "Test Bistro",
                "location": "Koramangala",
                "cuisines": ["Italian"],
                "rating": 4.5,
                "estimated_cost_for_two": 600.0,
                "budget_band": "medium",
                "attributes": {"city": "Bangalore"},
            },
            {
                "id": "def456",
                "name": "Spice Hub",
                "location": "Indiranagar",
                "cuisines": ["Indian", "Chinese"],
                "rating": 4.0,
                "estimated_cost_for_two": 300.0,
                "budget_band": "low",
                "attributes": {},
            },
        ]
    )
    df.to_parquet(path, index=False)
    return path


def test_store_load_and_query(sample_parquet: Path):
    store = RestaurantStore.load(sample_parquet)
    assert len(store) == 2
    assert store.get_by_id("abc123") is not None
    assert store.get_by_id("missing") is None

    cities = store.list_cities()
    assert "Koramangala" in cities
    assert "Bangalore" in cities

    all_rows = store.query_all()
    assert len(all_rows) == 2


def test_store_missing_file(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        RestaurantStore.load(tmp_path / "nope.parquet")


def test_store_empty_file(tmp_path: Path):
    path = tmp_path / "empty.parquet"
    pd.DataFrame(
        columns=[
            "id",
            "name",
            "location",
            "cuisines",
            "rating",
            "estimated_cost_for_two",
            "budget_band",
            "attributes",
        ]
    ).to_parquet(path, index=False)
    with pytest.raises(ValueError, match="No restaurants"):
        RestaurantStore.load(path)
