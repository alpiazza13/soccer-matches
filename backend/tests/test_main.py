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
from tests.conftest import MockTimeProvider, MockDatetimeProvider, client_with_db
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
    res = client_with_db.get("/matches", params={"user_id": 1})
    assert res.status_code == 200
    assert res.json() == []


def test_matches_endpoint_returns_match(client_with_db, persisted_match):
    """GET /matches should return serialized matches from DB using MatchSchema."""
    res = client_with_db.get("/matches", params={"user_id": 1})
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list) and len(body) == 1
    
    # Manually add the expected default is_done=False to comparison
    expected = MatchSchema.model_validate(persisted_match).model_dump(by_alias=True, mode='json')
    expected["is_done"] = False 
    assert body[0] == expected

def test_read_matches_with_is_done_status(client_with_db, persisted_match, user_payload):
    """Verify that the match list correctly reflects the is_done status for a specific user."""
    # 1. Create a user
    payload = user_payload(email="checker@example.com")
    user_res = client_with_db.post("/users", json=payload)
    user_id = user_res.json()["id"]

    # 2. Check matches initially (is_done should be False)
    res_before = client_with_db.get("/matches", params={"user_id": user_id})
    assert res_before.json()[0]["is_done"] is False

    # 3. Mark that match as done
    client_with_db.post(f"/matches/{persisted_match.external_id}/done", params={"user_id": user_id})

    # 4. Check matches again (is_done should now be True)
    res_after = client_with_db.get("/matches", params={"user_id": user_id})
    assert res_after.json()[0]["is_done"] is True