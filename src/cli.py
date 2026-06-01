"""Optional CLI smoke entry for Phase 5 orchestration."""

from __future__ import annotations

import argparse
import json
import sys

from src.services import RecommendationService, RecommendationServiceError


def main() -> int:
    parser = argparse.ArgumentParser(description="Restaurant recommendation CLI")
    parser.add_argument("--location", required=True)
    parser.add_argument("--budget", required=True, choices=["low", "medium", "high"])
    parser.add_argument("--cuisine")
    parser.add_argument("--min-rating", type=float, dest="min_rating")
    parser.add_argument("--additional", nargs="*", default=[])
    args = parser.parse_args()

    payload = {
        "location": args.location,
        "budget": args.budget,
        "cuisine": args.cuisine,
        "min_rating": args.min_rating,
        "additional_preferences": args.additional,
    }

    service = RecommendationService.from_defaults()
    try:
        response = service.recommend(payload)
    except RecommendationServiceError as exc:
        print(json.dumps(exc.to_dict(), indent=2))
        return 1

    print(response.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
