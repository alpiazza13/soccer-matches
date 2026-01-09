"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from datetime import datetime
from types import SimpleNamespace

from app.main import app
from app.services.football_api import FootballAPIClient
from tests.conftest import MockTimeProvider, MockDatetimeProvider


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
    res = client_with_db.get("/matches")
    assert res.status_code == 200
    body = res.json()
    assert isinstance(body, list) and len(body) == 1
    assert body[0]["is_done"] is False

    expected_id = persisted_match.external_id
    assert body[0]["external_id"] == expected_id

def test_read_matches_with_is_done_status(client_with_db, persisted_match, user_payload):
    """Verify that the match list correctly reflects the is_done status for a specific user."""
    user_res = client_with_db.post("/users", json=user_payload())
    user_id = user_res.json()["id"]

    res_before = client_with_db.get("/matches", params={"user_id": user_id})
    assert res_before.json()[0]["is_done"] is False

    # Mark  match as done
    client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"user_id": user_id, "is_done": True})

    res_after = client_with_db.get("/matches", params={"user_id": user_id})
    assert res_after.json()[0]["is_done"] is True


def test_read_matches_guest_access(client_with_db, persisted_match):
    """Verify that omitting user_id allows guest access with is_done=False."""
    res = client_with_db.get("/matches")
    
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["is_done"] is False

def test_read_matches_pagination_and_filtering(client_with_db, persisted_match, user_payload):
    user_id = client_with_db.post("/users", json=user_payload()).json()["id"]
    
    res_limit = client_with_db.get("/matches", params={"user_id": user_id, "limit": 0})
    assert len(res_limit.json()) == 0

    client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"user_id": user_id, "is_done": True})
    
    res_show = client_with_db.get("/matches", params={"user_id": user_id, "hide_done": False})
    assert len(res_show.json()) == 1
    
    res_hide = client_with_db.get("/matches", params={"user_id": user_id, "hide_done": True})
    assert len(res_hide.json()) == 0

def test_matches_pagination_offset(client_with_db, persisted_match):
    """Verify that an offset greater than total records returns an empty list."""
    res = client_with_db.get("/matches", params={"offset": 10})
    assert res.status_code == 200
    assert res.json() == []