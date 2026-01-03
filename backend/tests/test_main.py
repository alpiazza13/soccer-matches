"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from datetime import datetime
from types import SimpleNamespace

from app.main import app, get_db
from app.dependencies import get_football_api_client
from app.services.football_api import FootballAPIClient
from tests.conftest import MockTimeProvider, MockDatetimeProvider
from app.schemas import MatchSchema


@pytest.fixture
def client():
    """Fixture providing a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_football_client(api_token: str, mock_http_session: Mock, mock_time_provider: MockTimeProvider, mock_datetime_provider: MockDatetimeProvider, sample_api_response: dict):
    """Fixture providing a mocked FootballAPIClient."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = sample_api_response
    mock_http_session.get.return_value = mock_response
    
    return FootballAPIClient(
        api_token=api_token,
        http_session=mock_http_session,
        time_provider=mock_time_provider,
        datetime_provider=mock_datetime_provider
    )


class TestRootEndpoint:
    """Test suite for root endpoint."""
    
    def test_root_endpoint(self, client: TestClient):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Soccer Match Tracker API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data


class TestHealthEndpoint:
    """Test suite for health check endpoint."""
    
    def test_health_endpoint(self, client: TestClient):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


def test_matches_endpoint_empty(client_with_db):
    """GET /matches should return an empty list when DB has no matches."""
    res = client_with_db.get("/matches")
    assert res.status_code == 200
    assert res.json() == []


def test_matches_endpoint_returns_match(client_with_db, persisted_match):
    """GET /matches should return serialized matches from DB using MatchSchema."""
    with TestClient(app) as client_local:
        res = client_local.get("/matches")
        assert res.status_code == 200
        body = res.json()
        assert isinstance(body, list) and len(body) == 1
        expected = MatchSchema.model_validate(persisted_match).model_dump(by_alias=True, mode='json')
        assert body[0] == expected

