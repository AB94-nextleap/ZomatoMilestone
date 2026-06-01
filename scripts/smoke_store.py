#!/usr/bin/env python
"""Smoke test: load store and print row count + sample cities (Phase 1 task 1.10)."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.store.restaurant_store import RestaurantStore


def main() -> int:
    try:
        store = RestaurantStore.load()
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    cities = store.list_cities()
    print(f"Loaded {len(store):,} restaurants from {store.source_path}")
    print(f"Unique locations/cities: {len(cities):,}")
    print("Sample locations:", ", ".join(cities[:15]))
    if len(cities) > 15:
        print("  ...")

    sample = store.query_all()[:3]
    print("\nSample restaurants:")
    for r in sample:
        cost = r.estimated_cost_for_two if r.estimated_cost_for_two is not None else "N/A"
        print(f"  - {r.name} | {r.location} | {r.rating} | {r.budget_band} | cost={cost}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
