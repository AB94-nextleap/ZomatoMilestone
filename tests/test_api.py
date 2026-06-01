"""Integration tests for FastAPI recommendation endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import src.app.api as api
from src.models.restaurant import Restaurant
from src.services.recommendation_service import RecommendationService
from src.store.restaurant_store import RestaurantStore


class _FakeAdapter:
    def complete(self, messages: list[dict[str, str]]) -> str:  # noqa: ARG002
        return """
        {
          "summary": "AI recommendation",
          "recommendations": [
            {"id": "r1", "rank": 1, "explanation": "fits", "preference_matches": ["budget"]}
          ]
        }
        """


@pytest.fixture
def test_client() -> TestClient:
    # Setup test store and service
    r1 = Restaurant(
        id="r1",
        name="Pizza Place",
        location="Koramangala",
        cuisines=["Italian"],
        rating=4.5,
        estimated_cost_for_two=800.0,
        budget_band="medium",
        attributes={"city": "Bangalore"},
    )
    store = RestaurantStore([r1])
    service = RecommendationService(
        store=store,
        adapter_factory=lambda: _FakeAdapter(),
    )
    
    # Inject test service
    api._service = service
    client = TestClient(api.app)
    yield client
    
    # Reset service
    api._service = None


def test_health(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["restaurant_count"] == 1


def test_meta(test_client: TestClient):
    response = test_client.get("/api/v1/meta")
    assert response.status_code == 200
    data = response.json()
    assert "locations" in data
    assert "cuisines" in data
    assert "Koramangala" in data["locations"]
    assert "Italian" in data["cuisines"]


def test_metadata_locations(test_client: TestClient):
    response = test_client.get("/api/v1/metadata/locations")
    assert response.status_code == 200
    locations = response.json()
    assert isinstance(locations, list)
    assert "Koramangala" in locations
    assert "Bangalore" in locations


def test_metadata_cuisines(test_client: TestClient):
    response = test_client.get("/api/v1/metadata/cuisines")
    assert response.status_code == 200
    cuisines = response.json()
    assert isinstance(cuisines, list)
    assert "Italian" in cuisines


def test_recommend_success(test_client: TestClient):
    response = test_client.post(
        "/api/v1/recommend",
        json={
            "location": "Koramangala",
            "budget": "medium",
            "cuisine": "Italian",
            "min_rating": 4.0,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_count"] == 1
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["restaurant"]["id"] == "r1"


def test_recommend_validation_error(test_client: TestClient):
    response = test_client.post(
        "/api/v1/recommend",
        json={
            "location": "Koramangala",
            "budget": "invalid-budget",
        }
    )
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error_code"] == "VALIDATION_ERROR"
    assert data["field"] == "budget"


def test_recommend_no_candidates(test_client: TestClient):
    response = test_client.post(
        "/api/v1/recommend",
        json={
            "location": "Koramangala",
            "budget": "low",  # medium is available, low will return zero candidates
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["candidate_count"] == 0
    assert data["recommendations"] == []
    assert len(data["suggestions"]) > 0

