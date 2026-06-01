"""FastAPI application for Zomato AI Restaurant Advisor."""

from __future__ import annotations

import logging
import os
from typing import Any, Literal
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from src.services.recommendation_service import RecommendationService, RecommendationServiceError

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Zomato AI REST API",
    description="Backend recommendation endpoints for Zomato AI Restaurant Advisor",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RecommendationService instance (lazy load or load at startup)
_service: RecommendationService | None = None

def get_service() -> RecommendationService:
    global _service
    if _service is None:
        _service = RecommendationService.from_defaults()
    return _service


@app.exception_handler(RecommendationServiceError)
async def recommendation_service_error_handler(
    request: Request,
    exc: RecommendationServiceError,
) -> JSONResponse:
    """Map service errors to standard HTTP status codes."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    if exc.error_code == "VALIDATION_ERROR":
        status_code = status.HTTP_400_BAD_REQUEST
    elif exc.error_code == "NO_CANDIDATES":
        status_code = status.HTTP_404_NOT_FOUND
    elif exc.error_code == "DATA_UNAVAILABLE":
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif exc.error_code == "LLM_UNAVAILABLE":
        status_code = status.HTTP_502_BAD_GATEWAY

    return JSONResponse(
        status_code=status_code,
        content=exc.to_dict(),
    )


class RecommendRequest(BaseModel):
    location: str
    budget: str
    cuisine: str | None = None
    min_rating: float | None = None
    additional_preferences: list[str] = Field(default_factory=list)
    top_k: int | None = None


@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Check system health and store presence."""
    try:
        service = get_service()
        store_count = len(service.store.query_all())
        return {
            "status": "healthy",
            "store_loaded": True,
            "restaurant_count": store_count,
            "llm_configured": bool(os.getenv("GROQ_API_KEY") or os.getenv("LLM_API_KEY")),
        }
    except Exception as exc:
        logger.exception("Health check failed.")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "error": str(exc),
                "detail": "Data store missing or corrupt. Run 'python scripts/ingest.py' first.",
            },
        )


@app.get("/api/v1/meta")
async def get_metadata() -> dict[str, Any]:
    """Retrieve supported cities and unique cuisines to populate UI dropdowns."""
    try:
        service = get_service()
        locations = service.store.list_cities()
        
        # Extract unique sorted cuisines from dataset vocabulary
        all_cuisines = set()
        for r in service.store.query_all():
            for c in r.cuisines:
                if c and c.strip():
                    all_cuisines.add(c.strip())
                    
        return {
            "locations": locations,
            "cuisines": sorted(list(all_cuisines)),
        }
    except Exception as exc:
        logger.exception("Failed to retrieve metadata.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Failed to retrieve metadata: {exc}"},
        )


@app.get("/api/v1/metadata/locations")
async def get_locations() -> Any:
    """Retrieve unique locations/neighborhoods (e.g. Indiranagar, Bellandur) and parent cities."""
    try:
        service = get_service()
        return service.store.list_cities()
    except Exception as exc:
        logger.exception("Failed to retrieve locations metadata.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Failed to retrieve locations: {exc}"},
        )


@app.get("/api/v1/metadata/cuisines")
async def get_cuisines() -> Any:
    """Retrieve unique cuisines for dropdown select options."""
    try:
        service = get_service()
        all_cuisines = set()
        for r in service.store.query_all():
            for c in r.cuisines:
                if c and c.strip():
                    all_cuisines.add(c.strip())
        return sorted(list(all_cuisines))
    except Exception as exc:
        logger.exception("Failed to retrieve cuisines metadata.")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"success": False, "message": f"Failed to retrieve cuisines: {exc}"},
        )


@app.post("/api/v1/recommend")
async def recommend(req: RecommendRequest) -> dict[str, Any]:
    """Accept preference parameters and return grounded restaurant recommendations."""
    service = get_service()
    
    # Override top_k if specified in request
    if req.top_k is not None:
        service = RecommendationService(
            store=service.store,
            validator=service.validator,
            adapter_factory=service.adapter_factory,
            top_k=req.top_k,
        )
        
    payload = {
        "location": req.location,
        "budget": req.budget,
        "cuisine": req.cuisine,
        "min_rating": req.min_rating,
        "additional_preferences": req.additional_preferences,
    }
    
    response = service.recommend(payload)
    return response.model_dump()


# Mount Static Files for SPA Frontend
STATIC_DIR = Path(__file__).resolve().parent / "static"
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=str(STATIC_DIR), html=True), name="static")
else:
    logger.warning("Frontend static directory not found at: %s", STATIC_DIR)
