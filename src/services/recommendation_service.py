"""Phase 5 orchestration service: validate -> filter -> LLM -> response."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any, Callable

from src.config.loader import get_settings
from src.filters.candidate_builder import build_candidates
from src.llm.adapter import GroqLLMAdapter, LLMAdapter
from src.llm.engine import run_recommendation_engine
from src.models.recommendation import RecommendationResponse
from src.store.restaurant_store import RestaurantStore
from src.validation.errors import PreferenceValidationError
from src.validation.preferences_validator import PreferencesValidator

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class RecommendationServiceError(Exception):
    message: str
    error_code: str
    field: str | None = None
    suggestions: list[str] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": False,
            "error_code": self.error_code,
            "message": self.message,
            "field": self.field,
            "suggestions": self.suggestions or [],
        }


def _default_adapter_factory() -> LLMAdapter:
    settings = get_settings()
    provider = str(settings.get("llm_provider", "groq")).lower()
    if provider == "groq":
        return GroqLLMAdapter(model=str(settings.get("llm_model", "llama-3.3-70b-versatile")))
    raise RecommendationServiceError(
        message=f"Unsupported llm_provider '{provider}'.",
        error_code="CONFIG_ERROR",
    )


class RecommendationService:
    """Single entry-point for recommendation use-case orchestration."""

    def __init__(
        self,
        *,
        store: RestaurantStore,
        validator: PreferencesValidator | None = None,
        adapter_factory: Callable[[], LLMAdapter] | None = None,
        top_k: int | None = None,
    ) -> None:
        self.store = store
        self.validator = validator or PreferencesValidator(store)
        self.adapter_factory = adapter_factory or _default_adapter_factory
        settings = get_settings()
        self.top_k = top_k if top_k is not None else int(settings.get("top_k", 5))

    @classmethod
    def from_defaults(cls) -> RecommendationService:
        store = RestaurantStore.load()
        return cls(store=store)

    def recommend(self, raw_preferences: dict[str, Any]) -> RecommendationResponse:
        """
        Run end-to-end recommendation flow for validated user preferences.

        Raises RecommendationServiceError for user-safe failure cases.
        """
        t0 = time.perf_counter()
        try:
            prefs = self.validator.validate(raw_preferences)
        except PreferenceValidationError as exc:
            raise RecommendationServiceError(
                message=exc.message,
                error_code=exc.error_code,
                field=exc.field,
                suggestions=exc.suggestions,
            ) from exc

        try:
            t_validate = time.perf_counter()
            candidates_result = build_candidates(prefs, self.store)
            t_filter = time.perf_counter()

            if not candidates_result.candidates:
                logger.info(
                    "recommendation.empty candidates=0 validate_ms=%d filter_ms=%d",
                    int((t_validate - t0) * 1000),
                    int((t_filter - t_validate) * 1000),
                )
                return RecommendationResponse(
                    query=prefs,
                    candidate_count=0,
                    summary="No restaurants match your current filters.",
                    recommendations=[],
                    suggestions=candidates_result.suggestions,
                )

            adapter = self.adapter_factory()
            llm_started = time.perf_counter()
            response = run_recommendation_engine(
                prefs=prefs,
                candidates=candidates_result.candidates,
                adapter=adapter,
                top_k=self.top_k,
            )
            llm_done = time.perf_counter()

            logger.info(
                "recommendation.success candidates=%d returned=%d validate_ms=%d filter_ms=%d llm_ms=%d total_ms=%d",
                len(candidates_result.candidates),
                len(response.recommendations),
                int((t_validate - t0) * 1000),
                int((t_filter - t_validate) * 1000),
                int((llm_done - llm_started) * 1000),
                int((llm_done - t0) * 1000),
            )
            return response
        except Exception as exc:
            logger.exception("Unexpected error in recommendation service pipeline.")
            raise RecommendationServiceError(
                message="Something went wrong. Please try again later.",
                error_code="INTERNAL_ERROR",
            ) from exc
