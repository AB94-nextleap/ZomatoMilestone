# Data Schema: ManikaSaini/zomato-restaurant-recommendation

Source: [Hugging Face dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) (~51,717 rows).

## Raw columns (17)

| Column | Type | Used in canonical model |
|--------|------|-------------------------|
| `url` | string | `attributes.url` |
| `address` | string | `attributes.address`; city inference |
| `name` | string | `name` |
| `online_order` | string | `attributes.online_order` |
| `book_table` | string | `attributes.book_table` |
| `rate` | string | `rating` (parsed, e.g. `4.1/5`) |
| `votes` | int64 | `attributes.votes` |
| `phone` | string | — |
| `location` | string | `attributes.locality` |
| `rest_type` | string | `attributes.rest_type` |
| `dish_liked` | string | — |
| `cuisines` | string | `cuisines` (split list) |
| `approx_cost(for two people)` | string | `estimated_cost_for_two`, `budget_band` |
| `reviews_list` | string | — (Phase 4+ optional) |
| `menu_item` | string | — |
| `listed_in(type)` | string | `attributes.listed_in_type` |
| `listed_in(city)` | string | **`location`** (primary area) |

## Canonical `Restaurant` (parquet)

Written to `data/restaurants.parquet` by `scripts/ingest.py`.

| Field | Type | Notes |
|-------|------|--------|
| `id` | string | SHA-256 prefix of name + location + address |
| `name` | string | Required |
| `location` | string | From `listed_in(city)`, else `location` |
| `cuisines` | list[string] | Comma-separated split |
| `rating` | float | 0–5; invalid/`NEW`/`-` rows skipped |
| `estimated_cost_for_two` | float \| null | Parsed; ranges use lower bound |
| `budget_band` | string | `low` \| `medium` \| `high` \| `unknown` |
| `attributes` | object | locality, city, address, url, votes, etc. |

## Budget bands

From `config/budget_bands.yaml` (INR, cost for two):

| Band | Rule |
|------|------|
| low | cost &lt; 500 |
| medium | 500 ≤ cost &lt; 1500 |
| high | cost ≥ 1500 |
| unknown | missing cost |

## Ingest metadata

`data/restaurants.meta.json` — `ingested_at`, `dataset`, `row_count`.

## Normalization rules

- **Rating:** strip `/5`, reject `NEW`, `-`, empty
- **Cost:** remove `₹`, commas; `300-400` → 300
- **Location:** title-case; aliases `Bengaluru` → `Bangalore` in city field
- **Dedup:** same `(name, location)` → keep highest `rating`

See `src/ingest/preprocessor.py` for implementation.
