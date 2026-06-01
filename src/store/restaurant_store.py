"""Load and query normalized restaurants from parquet (architecture §3.2)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.config.loader import PROJECT_ROOT, get_settings
from src.models.restaurant import Restaurant


class RestaurantStore:
    """In-memory restaurant store backed by parquet."""

    def __init__(self, restaurants: list[Restaurant], source_path: Path | None = None) -> None:
        self._restaurants = restaurants
        self._by_id = {r.id: r for r in restaurants}
        self._source_path = source_path
        self._df: pd.DataFrame | None = None

    @property
    def source_path(self) -> Path | None:
        return self._source_path

    @classmethod
    def load(cls, data_path: str | Path | None = None) -> RestaurantStore:
        path = Path(data_path) if data_path else Path(get_settings()["data_path"])
        if not path.is_absolute():
            path = PROJECT_ROOT / path

        if not path.exists():
            raise FileNotFoundError(
                f"Restaurant data not found at {path}. "
                "Run: python scripts/ingest.py"
            )

        df = pd.read_parquet(path)
        required = {
            "id",
            "name",
            "location",
            "cuisines",
            "rating",
            "estimated_cost_for_two",
            "budget_band",
        }
        missing = required - set(df.columns)
        if missing:
            raise ValueError(f"Parquet missing columns: {sorted(missing)}")

        restaurants: list[Restaurant] = []
        for record in df.to_dict(orient="records"):
            cuisines_raw = record.get("cuisines")
            if isinstance(cuisines_raw, str):
                cuisines = json.loads(cuisines_raw)
            elif isinstance(cuisines_raw, (list, set, tuple)):
                cuisines = list(cuisines_raw)
            elif hasattr(cuisines_raw, "tolist"):
                cuisines = cuisines_raw.tolist()
            else:
                cuisines = []

            attributes_raw = record.get("attributes")
            if isinstance(attributes_raw, str):
                attributes = json.loads(attributes_raw)
            elif isinstance(attributes_raw, dict):
                attributes = dict(attributes_raw)
            else:
                attributes = {}

            restaurants.append(
                Restaurant(
                    id=str(record["id"]),
                    name=str(record["name"]),
                    location=str(record["location"]),
                    cuisines=cuisines,
                    rating=float(record["rating"]),
                    estimated_cost_for_two=(
                        None
                        if pd.isna(record.get("estimated_cost_for_two"))
                        else float(record["estimated_cost_for_two"])
                    ),
                    budget_band=record.get("budget_band") or "unknown",
                    attributes=attributes,
                )
            )

        if not restaurants:
            raise ValueError(f"No restaurants loaded from {path}")

        return cls(restaurants, source_path=path)

    def __len__(self) -> int:
        return len(self._restaurants)

    def get_by_id(self, restaurant_id: str) -> Restaurant | None:
        return self._by_id.get(restaurant_id)

    def list_cities(self) -> list[str]:
        """Unique normalized locations (areas/cities) for validation UI."""
        locations = {r.location for r in self._restaurants if r.location}
        cities = {
            r.attributes["city"]
            for r in self._restaurants
            if r.attributes.get("city")
        }
        return sorted(locations | cities)

    def query_all(self) -> list[Restaurant]:
        return list(self._restaurants)

    def to_dataframe(self) -> pd.DataFrame:
        if self._df is None:
            self._df = pd.DataFrame([r.model_dump() for r in self._restaurants])
        return self._df
