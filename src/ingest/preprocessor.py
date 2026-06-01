"""Normalize raw Hugging Face Zomato rows into canonical Restaurant records."""

from __future__ import annotations

import hashlib
import re
from typing import Any

from src.config.loader import load_budget_bands
from src.models.restaurant import BudgetBand, Restaurant

# Raw dataset columns (ManikaSaini/zomato-restaurant-recommendation)
RAW_COLUMNS = [
    "url",
    "address",
    "name",
    "online_order",
    "book_table",
    "rate",
    "votes",
    "phone",
    "location",
    "rest_type",
    "dish_liked",
    "cuisines",
    "approx_cost(for two people)",
    "reviews_list",
    "menu_item",
    "listed_in(type)",
    "listed_in(city)",
]

_CITY_ALIASES: dict[str, str] = {
    "bengaluru": "Bangalore",
    "bangalore": "Bangalore",
    "banglore": "Bangalore",
    "bangluru": "Bangalore",
}

_INVALID_RATINGS = frozenset({"new", "-", "nan", "none", ""})


def _clean_str(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in ("nan", "none", "null"):
        return None
    return text


def normalize_location(value: str | None) -> str | None:
    """Normalize area/city names for consistent filtering."""
    text = _clean_str(value)
    if not text:
        return None
    key = text.lower()
    if key in _CITY_ALIASES:
        return _CITY_ALIASES[key]
    return text.title() if text.islower() else text


def parse_rating(raw: Any) -> float | None:
    text = _clean_str(raw)
    if not text:
        return None
    lowered = text.lower()
    if lowered in _INVALID_RATINGS:
        return None
    match = re.search(r"(\d+(?:\.\d+)?)", text.replace("/5", ""))
    if not match:
        return None
    rating = float(match.group(1))
    if rating < 0 or rating > 5:
        return None
    return rating


def parse_cost(raw: Any) -> float | None:
    """Parse approx cost; handles ranges by taking the lower bound."""
    text = _clean_str(raw)
    if not text:
        return None
    text = text.replace(",", "").replace("₹", "").strip()
    if "-" in text:
        parts = text.split("-", 1)
        text = parts[0].strip()
    numbers = re.findall(r"\d+(?:\.\d+)?", text)
    if not numbers:
        return None
    return float(numbers[0])


def parse_cuisines(raw: Any) -> list[str]:
    text = _clean_str(raw)
    if not text:
        return []
    parts = re.split(r"[,|/]", text)
    seen: set[str] = set()
    result: list[str] = []
    for part in parts:
        token = part.strip()
        if not token:
            continue
        key = token.lower()
        if key not in seen:
            seen.add(key)
            result.append(token)
    return result


def infer_city_from_address(address: str | None) -> str | None:
    if not address:
        return None
    lower = address.lower()
    for alias, canonical in _CITY_ALIASES.items():
        if alias in lower:
            return canonical
    return None


def compute_budget_band(cost: float | None, bands: dict[str, dict[str, float]] | None = None) -> BudgetBand:
    if cost is None:
        return "unknown"
    if bands is None:
        bands = load_budget_bands()

    low_max = bands.get("low", {}).get("max", 500)
    medium_min = bands.get("medium", {}).get("min", 500)
    medium_max = bands.get("medium", {}).get("max", 1500)
    high_min = bands.get("high", {}).get("min", 1500)

    if cost < low_max:
        return "low"
    if cost < medium_max:
        return "medium"
    if cost >= high_min:
        return "high"
    if cost >= medium_min:
        return "medium"
    return "unknown"


def make_restaurant_id(name: str, location: str, address: str | None = None) -> str:
    key = f"{name.strip().lower()}|{location.strip().lower()}|{(address or '').strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def preprocess_row(row: dict[str, Any], bands: dict[str, dict[str, float]] | None = None) -> Restaurant | None:
    """
    Convert one raw dataset row to Restaurant, or None if row should be skipped.
    Skips rows missing name, location, or valid rating (ING-04, ING-05).
    """
    name = _clean_str(row.get("name"))
    if not name:
        return None

    area = normalize_location(row.get("listed_in(city)"))
    locality = normalize_location(row.get("location"))
    location = area or locality
    if not location:
        return None

    rating = parse_rating(row.get("rate"))
    if rating is None:
        return None

    cost = parse_cost(row.get("approx_cost(for two people)"))
    cuisines = parse_cuisines(row.get("cuisines"))
    address = _clean_str(row.get("address"))
    city = infer_city_from_address(address)

    restaurant_id = make_restaurant_id(name, location, address)
    budget_band = compute_budget_band(cost, bands)

    attributes: dict[str, Any] = {
        "locality": locality,
        "city": city,
        "address": address,
        "url": _clean_str(row.get("url")),
        "votes": row.get("votes"),
        "rest_type": _clean_str(row.get("rest_type")),
        "online_order": _clean_str(row.get("online_order")),
        "book_table": _clean_str(row.get("book_table")),
        "listed_in_type": _clean_str(row.get("listed_in(type)")),
    }
    attributes = {k: v for k, v in attributes.items() if v is not None}

    return Restaurant(
        id=restaurant_id,
        name=name,
        location=location,
        cuisines=cuisines,
        rating=rating,
        estimated_cost_for_two=cost,
        budget_band=budget_band,
        attributes=attributes,
    )


def preprocess_dataset(rows: list[dict[str, Any]]) -> tuple[list[Restaurant], dict[str, int]]:
    """
    Preprocess all rows with deduplication by (name, location), keeping highest rating.
    Returns restaurants and ingest statistics.
    """
    bands = load_budget_bands()
    stats = {
        "total_rows": len(rows),
        "ingested": 0,
        "skipped": 0,
        "duplicates_removed": 0,
    }
    best_by_key: dict[tuple[str, str], Restaurant] = {}

    for row in rows:
        restaurant = preprocess_row(row, bands=bands)
        if restaurant is None:
            stats["skipped"] += 1
            continue

        key = (restaurant.name.lower(), restaurant.location.lower())
        existing = best_by_key.get(key)
        if existing is None:
            best_by_key[key] = restaurant
        elif restaurant.rating > existing.rating:
            best_by_key[key] = restaurant
            stats["duplicates_removed"] += 1
        else:
            stats["duplicates_removed"] += 1

    restaurants = list(best_by_key.values())
    stats["ingested"] = len(restaurants)
    return restaurants, stats
