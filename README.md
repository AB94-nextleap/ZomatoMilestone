# Zomato AI Restaurant Recommendation System

AI-powered restaurant recommendations using the [Zomato Hugging Face dataset](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant-recommendation) and an LLM (later phases).

## Documentation

- [`context.md`](context.md) — product requirements
- [`architecture.md`](architecture.md) — system design
- [`implementation-plan.md`](implementation-plan.md) — phased build plan
- [`edge-cases.md`](edge-cases.md) — edge case handling
- [`docs/data-schema.md`](docs/data-schema.md) — raw → canonical column mapping

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Phase 1: Data ingestion

```bash
python scripts/ingest.py
python scripts/smoke_store.py
```

Produces `data/restaurants.parquet` and `data/restaurants.meta.json`.

## Phase 3: Filter & candidate builder

```python
from src.store.restaurant_store import RestaurantStore
from src.validation import PreferencesValidator
from src.filters import build_candidates

store = RestaurantStore.load()
prefs = PreferencesValidator(store).validate({
    "location": "Bangalore",
    "budget": "medium",
    "cuisine": "Italian",
    "min_rating": 4.0,
})
result = build_candidates(prefs, store)
print(len(result.candidates), result.suggestions)
```

## Phase 4: Groq LLM engine

```python
from src.llm import GroqLLMAdapter, run_recommendation_engine

adapter = GroqLLMAdapter()  # requires GROQ_API_KEY
response = run_recommendation_engine(
    prefs=prefs,
    candidates=result.candidates,
    adapter=adapter,
    top_k=5,
)
print(response.summary)
```

Manual smoke test:

```bash
python scripts/smoke_llm.py
```

## Phase 5: Orchestration service

```python
from src.services import RecommendationService

service = RecommendationService.from_defaults()
response = service.recommend({
    "location": "Bangalore",
    "budget": "medium",
    "cuisine": "Italian",
    "min_rating": 4.0,
})
print(response.model_dump())
```

CLI smoke:

```bash
python -m src.cli --location Bangalore --budget medium --cuisine Italian --min-rating 4.0
```

## Phase 2: Preferences validation

```python
from src.store.restaurant_store import RestaurantStore
from src.validation import PreferencesValidator

store = RestaurantStore.load()
validator = PreferencesValidator(store)
prefs = validator.validate({
    "location": "Koramangala",
    "budget": "medium",
    "cuisine": "Italian",
    "min_rating": 4.0,
})
```

## Tests

```bash
pip install pytest
pytest tests/ -v
```

## Project layout

```
config/           # settings.yaml, budget_bands.yaml
data/             # generated parquet (gitignored)
docs/             # data-schema.md
scripts/          # ingest.py, smoke_store.py
src/
  config/         # config loader
  filters/        # deterministic candidate filtering
  ingest/         # preprocessing
  llm/            # Groq adapter, parser, engine, formatter, prompts
  models/         # Restaurant entity
  store/          # RestaurantStore
  validation/     # user input validation
tests/
```
