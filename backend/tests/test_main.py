"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import ANY, Mock, MagicMock

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
    user_email = user_res.json()["email"]

    res_before = client_with_db.get("/matches", params={"email": user_email})
    assert res_before.json()[0]["is_done"] is False

    # Mark  match as done
    client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"email": user_email, "is_done": True})

    res_after = client_with_db.get("/matches", params={"email": user_email})
    assert res_after.json()[0]["is_done"] is True


def test_read_matches_guest_access(client_with_db, persisted_match):
    """Verify that omitting user_id allows guest access with is_done=False."""
    res = client_with_db.get("/matches")
    
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    assert data[0]["is_done"] is False

def test_read_matches_pagination_and_filtering(client_with_db, persisted_match, user_payload):
    user_email = client_with_db.post("/users", json=user_payload()).json()["email"]
    
    res_limit = client_with_db.get("/matches", params={"email": user_email, "limit": 0})
    assert len(res_limit.json()) == 0

    client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"email": user_email, "is_done": True})

    res_show = client_with_db.get("/matches", params={"email": user_email, "hide_done": False})
    assert len(res_show.json()) == 1

    res_hide = client_with_db.get("/matches", params={"email": user_email, "hide_done": True})
    assert len(res_hide.json()) == 0

def test_matches_pagination_offset(client_with_db, persisted_match):
    """Verify that an offset greater than total records returns an empty list."""
    res = client_with_db.get("/matches", params={"offset": 10})
    assert res.status_code == 200
    assert res.json() == []



class TestSyncEndpoint:
    """Test suite for the manual database sync endpoint."""

    def test_trigger_sync_success(self, client_with_db, monkeypatch):
        """Verify the endpoint returns success when the sync function completes."""
        mock_perform = MagicMock()
        monkeypatch.setattr("app.main.get_sync_freshness", lambda db, key: False)
        monkeypatch.setattr("app.main.perform_sync", mock_perform)
        monkeypatch.setattr("app.main.update_sync_metadata", MagicMock())
        monkeypatch.setattr("app.main.is_syncing_globally", False)
        
        response = client_with_db.post("/api/matches/sync")
        
        assert response.status_code == 200
        assert response.json() == {
            "success": True, 
            "message": "Database synced successfully"
        }
        mock_perform.assert_called_once()

    def test_trigger_sync_skipped_when_fresh(self, client_with_db, monkeypatch):
        """Verify sync is skipped if the service says data is already fresh."""
        mock_perform = MagicMock()
        monkeypatch.setattr("app.main.get_sync_freshness", lambda db, key: True)
        monkeypatch.setattr("app.main.perform_sync", mock_perform)
        
        response = client_with_db.post("/api/matches/sync")
        
        assert response.status_code == 200
        assert "already fresh" in response.json()["message"]
        mock_perform.assert_not_called()

    def test_trigger_sync_failure_releases_lock(self, client_with_db, monkeypatch):
        """Verify lock is released and metadata updated on failure."""
        mock_perform = MagicMock(side_effect=Exception("API Down"))
        mock_update = MagicMock()
        
        monkeypatch.setattr("app.main.get_sync_freshness", lambda db, key: False)
        monkeypatch.setattr("app.main.perform_sync", mock_perform)
        monkeypatch.setattr("app.main.update_sync_metadata", mock_update)
        
        # Mock DB methods to prevent transaction deassociation warnings
        monkeypatch.setattr("sqlalchemy.orm.Session.rollback", lambda x: None)
        monkeypatch.setattr("sqlalchemy.orm.Session.commit", lambda x: None)
        
        monkeypatch.setattr("app.main.is_syncing_globally", False)
        response = client_with_db.post("/api/matches/sync")
        assert response.status_code == 500
        
        # Verify metadata was updated with FAILED status
        mock_update.assert_called_with(ANY, "matches_sync", status="FAILED", error="API Down")

        # Verify lock was released by trying a second successful request
        mock_perform.side_effect = None
        response_two = client_with_db.post("/api/matches/sync")
        assert response_two.status_code == 200

    def test_trigger_sync_already_in_progress(self, client_with_db, monkeypatch):
        """Verify 429 is returned if the global lock is already active."""
        monkeypatch.setattr("app.main.is_syncing_globally", True)
        response = client_with_db.post("/api/matches/sync")
        assert response.status_code == 429
        assert "already in progress" in response.json()["detail"]