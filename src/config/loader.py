"""Load YAML configuration with optional environment overrides."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

CONFIG_DIR = PROJECT_ROOT / "config"


@lru_cache
def get_settings() -> dict[str, Any]:
    path = CONFIG_DIR / "settings.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Settings file not found: {path}")
    with path.open(encoding="utf-8") as f:
        settings = yaml.safe_load(f) or {}

    if data_path := os.getenv("DATA_PATH"):
        settings["data_path"] = data_path
    if llm_provider := os.getenv("LLM_PROVIDER"):
        settings["llm_provider"] = llm_provider
    if llm_model := os.getenv("LLM_MODEL"):
        settings["llm_model"] = llm_model

    return settings


@lru_cache
def load_budget_bands() -> dict[str, dict[str, float]]:
    path = CONFIG_DIR / "budget_bands.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Budget bands file not found: {path}")
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("bands", {})
