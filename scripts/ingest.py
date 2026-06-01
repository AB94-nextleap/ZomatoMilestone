#!/usr/bin/env python
"""
Load Zomato dataset from Hugging Face, normalize, and write data/restaurants.parquet.

Usage (from project root):
    python scripts/ingest.py
    python scripts/ingest.py --output data/restaurants.parquet
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd
from datasets import load_dataset

from src.ingest.preprocessor import RAW_COLUMNS, preprocess_dataset
from src.config.loader import get_settings

DATASET_ID = "ManikaSaini/zomato-restaurant-recommendation"


def load_raw_rows() -> list[dict]:
    print(f"Loading dataset: {DATASET_ID}")
    dataset = load_dataset(DATASET_ID, split="train")
    print(f"  Raw rows: {len(dataset):,}")
    missing_cols = [c for c in RAW_COLUMNS if c not in dataset.column_names]
    if missing_cols:
        raise ValueError(
            f"Dataset schema mismatch. Missing columns: {missing_cols}. "
            f"Found: {dataset.column_names}"
        )
    return [dict(row) for row in dataset]


def write_parquet(restaurants: list, output_path: Path) -> None:
    records = [r.model_dump() for r in restaurants]
    df = pd.DataFrame(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(".parquet.tmp")
    df.to_parquet(tmp_path, index=False)
    tmp_path.replace(output_path)

    meta = {
        "ingested_at": datetime.now(timezone.utc).isoformat(),
        "dataset": DATASET_ID,
        "row_count": len(df),
    }
    meta_path = output_path.with_suffix(".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest Zomato restaurant dataset")
    default_out = PROJECT_ROOT / get_settings()["data_path"]
    parser.add_argument(
        "--output",
        type=Path,
        default=default_out,
        help="Output parquet path",
    )
    args = parser.parse_args()

    try:
        rows = load_raw_rows()
        restaurants, stats = preprocess_dataset(rows)
    except Exception as exc:
        print(f"ERROR: Ingest failed: {exc}", file=sys.stderr)
        return 1

    if not restaurants:
        print("ERROR: No restaurants after preprocessing.", file=sys.stderr)
        return 1

    output_path = args.output
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path

    try:
        write_parquet(restaurants, output_path)
    except Exception as exc:
        print(f"ERROR: Failed to write parquet: {exc}", file=sys.stderr)
        return 1

    print("\nIngest summary")
    print(f"  Total rows:         {stats['total_rows']:,}")
    print(f"  Ingested:           {stats['ingested']:,}")
    print(f"  Skipped:            {stats['skipped']:,}")
    print(f"  Duplicates removed: {stats['duplicates_removed']:,}")
    print(f"  Output:             {output_path}")
    print(f"  Unique locations:   {len({r.location for r in restaurants}):,}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
