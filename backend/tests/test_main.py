"""
Integration tests for FastAPI endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, MagicMock
from datetime import datetime

from app.main import app
from app.dependencies import get_football_api_client
from app.services.football_api import FootballAPIClient
from tests.conftest import MockTimeProvider, MockDatetimeProvider


@pytest.fixture
def client():
    """Fixture providing a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_football_client(api_token, mock_http_session, mock_time_provider, mock_datetime_provider, sample_api_response):
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
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Soccer Match Tracker API"
        assert data["version"] == "1.0.0"
        assert "endpoints" in data


class TestHealthEndpoint:
    """Test suite for health check endpoint."""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


'''
class TestGetMatchesEndpoint:
    """Test suite for get-matches endpoint."""
    
    def test_get_matches_with_competition(self, client, mock_football_client):
        """Test get-matches endpoint with competition parameter."""
        # Override the dependency
        app.dependency_overrides[get_football_api_client] = lambda: mock_football_client
        
        try:
            response = client.get("/api/matches?competition=premier%20league")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["competition"] == "premier league"
            assert "matches" in data
            assert "matches_count" in data
        finally:
            # Clean up: remove the override
            app.dependency_overrides.clear()
    
    def test_get_matches_with_date_range(self, client, mock_football_client):
        """Test get-matches endpoint with date range."""
        # Override the dependency
        app.dependency_overrides[get_football_api_client] = lambda: mock_football_client
        
        try:
            response = client.get("/api/matches?date_from=2024-01-01&date_to=2024-01-31")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["date_range"]["from"] == "2024-01-01"
            assert data["date_range"]["to"] == "2024-01-31"
        finally:
            # Clean up: remove the override
            app.dependency_overrides.clear()
    
    def test_get_matches_all_competitions(self, client, mock_football_client):
        """Test get-matches endpoint without competition (all competitions)."""
        # Override the dependency
        app.dependency_overrides[get_football_api_client] = lambda: mock_football_client
        
        try:
            response = client.get("/api/matches")
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["competition"] == "all"
        finally:
            # Clean up: remove the override
            app.dependency_overrides.clear()
    
    def test_get_matches_invalid_competition(self, client, api_token):
        """Test get-matches endpoint with invalid competition."""
        # Create a mock client that raises ValueError
        mock_client = Mock(spec=FootballAPIClient)
        mock_client.get_matches.side_effect = ValueError("Unknown competition: invalid")
        
        # Override the dependency
        app.dependency_overrides[get_football_api_client] = lambda: mock_client
        
        try:
            response = client.get("/api/matches?competition=invalid")
            
            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
        finally:
            # Clean up: remove the override
            app.dependency_overrides.clear()
'''