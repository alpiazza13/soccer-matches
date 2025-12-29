"""
Unit tests for FootballAPIClient.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import requests

from app.services.football_api import FootballAPIClient


class TestFootballAPIClient:
    """Test suite for FootballAPIClient."""
    
    def test_init_with_api_token(self, api_token):
        """Test initialization with explicit API token."""
        client = FootballAPIClient(api_token=api_token)
        assert client.api_token == api_token
        assert client.headers == {"X-Auth-Token": api_token}
    
    def test_init_without_api_token_raises_error(self):
        """Test that initialization without API token raises ValueError."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="API token is required"):
                FootballAPIClient()
    
    def test_get_all_competitions(self, api_token):
        """Test getting list of all competitions."""
        client = FootballAPIClient(api_token=api_token)
        competitions = client.get_all_competitions()
        
        assert isinstance(competitions, list)
        assert len(competitions) == 8
        assert "premier league" in competitions
        assert "serie a" in competitions
        assert "champions league" in competitions
    
    def test_get_matches_invalid_competition(self, api_token, mock_http_session):
        """Test that invalid competition raises ValueError."""
        client = FootballAPIClient(
            api_token=api_token,
            http_session=mock_http_session
        )
        
        with pytest.raises(ValueError, match="Unknown competition"):
            client.get_matches(competition="invalid competition")
    
    def test_get_matches_success(
        self, 
        api_token, 
        mock_http_session, 
        mock_time_provider,
        mock_datetime_provider,
        sample_api_response
    ):
        """Test successful match fetching."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_http_session.get.return_value = mock_response
        
        # Create client with mocks
        client = FootballAPIClient(
            api_token=api_token,
            http_session=mock_http_session,
            time_provider=mock_time_provider,
            datetime_provider=mock_datetime_provider
        )
        
        # Fetch matches
        processed_matches, raw_matches = client.get_matches(
            competition="premier league",
            date_from="2024-01-01",
            date_to="2024-01-31"
        )
        
        # Verify API call
        mock_http_session.get.assert_called_once()
        call_args = mock_http_session.get.call_args
        assert "competitions/2021/matches" in call_args[0][0]
        assert call_args[1]["params"]["dateFrom"] == "2024-01-01"
        assert call_args[1]["params"]["dateTo"] == "2024-01-31"
        assert call_args[1]["headers"]["X-Auth-Token"] == api_token
        
        # Verify results
        assert len(processed_matches) == 1
        assert len(raw_matches) == 1
        
        match = processed_matches[0]
        assert match["match_id"] == 123456
        assert match["home_team"] == "Arsenal"
        assert match["away_team"] == "Chelsea"
        assert match["home_score"] == 2
        assert match["away_score"] == 1
        assert match["competition"] == "premier league"
        assert match["winner"] == "HOME_TEAM"
        assert "date_display" in match
        assert "time_display" in match
    
    def test_get_matches_default_date_range(
        self,
        api_token,
        mock_http_session,
        mock_time_provider,
        mock_datetime_provider,
        sample_api_response
    ):
        """Test that default date range is used when not provided."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_http_session.get.return_value = mock_response
        
        # Set datetime to a known value
        mock_datetime_provider.set_datetime(datetime(2024, 1, 15, 12, 0, 0))
        
        client = FootballAPIClient(
            api_token=api_token,
            http_session=mock_http_session,
            time_provider=mock_time_provider,
            datetime_provider=mock_datetime_provider
        )
        
        client.get_matches(competition="premier league")
        
        # Verify default dates were used
        call_args = mock_http_session.get.call_args
        params = call_args[1]["params"]
        assert params["dateFrom"] == "2024-01-08"  # 7 days before
        assert params["dateTo"] == "2024-01-15"  # today
    
    def test_rate_limiting(
        self,
        api_token,
        mock_http_session,
        mock_time_provider,
        mock_datetime_provider,
        sample_api_response
    ):
        """Test that rate limiting works correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_http_session.get.return_value = mock_response
        
        client = FootballAPIClient(
            api_token=api_token,
            http_session=mock_http_session,
            time_provider=mock_time_provider,
            datetime_provider=mock_datetime_provider
        )
        
        # First call - no sleep
        client.get_matches(competition="premier league", date_from="2024-01-01", date_to="2024-01-31")
        assert len(mock_time_provider.get_sleep_calls()) == 0
        
        # Second call immediately after - should sleep
        mock_time_provider.advance_time(1.0)  # Only 1 second passed
        client.get_matches(competition="serie a", date_from="2024-01-01", date_to="2024-01-31")
        assert len(mock_time_provider.get_sleep_calls()) > 0
        # Should sleep for approximately 5 seconds (6 - 1)
        sleep_duration = mock_time_provider.get_sleep_calls()[0]
        assert 4.9 <= sleep_duration <= 5.1
        
        # Third call after enough time - no sleep
        mock_time_provider.advance_time(10.0)  # Enough time passed
        client.get_matches(competition="bundesliga", date_from="2024-01-01", date_to="2024-01-31")
        # Should not add another sleep call
        assert len(mock_time_provider.get_sleep_calls()) == 1
    
    def test_get_matches_api_error(
        self,
        api_token,
        mock_http_session,
        mock_time_provider,
        mock_datetime_provider
    ):
        """Test handling of API errors."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("Server Error")
        mock_http_session.get.return_value = mock_response
        
        client = FootballAPIClient(
            api_token=api_token,
            http_session=mock_http_session,
            time_provider=mock_time_provider,
            datetime_provider=mock_datetime_provider
        )
        
        with pytest.raises(requests.exceptions.HTTPError):
            client.get_matches(
                competition="premier league",
                date_from="2024-01-01",
                date_to="2024-01-31"
            )
    
    def test_extract_match_info(self, api_token, sample_match_data):
        """Test match info extraction logic."""
        client = FootballAPIClient(api_token=api_token)
        
        match_info = client._extract_match_info(sample_match_data, "premier league")
        
        assert match_info["match_id"] == 123456
        assert match_info["home_team"] == "Arsenal"
        assert match_info["away_team"] == "Chelsea"
        assert match_info["home_score"] == 2
        assert match_info["away_score"] == 1
        assert match_info["competition"] == "premier league"
        assert match_info["winner"] == "HOME_TEAM"
        assert "date_display" in match_info
        assert "time_display" in match_info
        assert "match_date_utc" in match_info
        assert "match_date" in match_info
    
    def test_extract_match_info_time_formatting(self, api_token):
        """Test that time formatting works correctly."""
        client = FootballAPIClient(api_token=api_token)
        
        # Test match at 3:30 PM UTC (11:30 AM Eastern)
        match_data = {
            "id": 123,
            "utcDate": "2024-01-15T15:30:00Z",
            "homeTeam": {"shortName": "Team A"},
            "awayTeam": {"shortName": "Team B"},
            "score": {
                "fullTime": {"home": 1, "away": 0},
                "winner": "HOME_TEAM"
            }
        }
        
        match_info = client._extract_match_info(match_data, "premier league")
        
        # UTC 15:30 = Eastern 11:30 AM
        assert match_info["time_display"] == "11:30 AM"
        assert match_info["date_display"] == "1/15/2024"
    
    def test_fetch_all_matches(
        self,
        api_token,
        mock_http_session,
        mock_time_provider,
        mock_datetime_provider,
        sample_api_response
    ):
        """Test fetching matches from all competitions."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_api_response
        mock_http_session.get.return_value = mock_response
        
        client = FootballAPIClient(
            api_token=api_token,
            http_session=mock_http_session,
            time_provider=mock_time_provider,
            datetime_provider=mock_datetime_provider
        )
        
        # Mock time to advance quickly so rate limiting doesn't slow tests
        def advance_time_after_call(*args, **kwargs):
            mock_time_provider.advance_time(10.0)
            return mock_response
        
        mock_http_session.get.side_effect = advance_time_after_call
        
        processed_matches, raw_matches = client.fetch_all_matches(
            date_from="2024-01-01",
            date_to="2024-01-31"
        )
        
        # Should fetch from 8 competitions
        assert mock_http_session.get.call_count == 8
        assert len(processed_matches) == 8  # One match per competition
        assert len(raw_matches) == 8

