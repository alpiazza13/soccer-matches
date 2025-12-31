"""
Pytest configuration and shared fixtures.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from typing import Iterator

from app.utils.time_provider import TimeProvider, DatetimeProvider
from app.services.football_api import FootballAPIClient


class MockTimeProvider(TimeProvider):
    """Mock time provider for testing."""
    
    def __init__(self):
        self._current_time = 1000.0
        self._sleep_calls = []
    
    def time(self) -> float:
        return self._current_time
    
    def set_time(self, time: float):
        """Set the current time."""
        self._current_time = time
    
    def advance_time(self, seconds: float):
        """Advance the current time by the given seconds."""
        self._current_time += seconds
    
    def sleep(self, seconds: float) -> None:
        """Record sleep calls instead of actually sleeping."""
        self._sleep_calls.append(seconds)
        self._current_time += seconds
    
    def get_sleep_calls(self):
        """Get list of sleep calls."""
        return self._sleep_calls


class MockDatetimeProvider(DatetimeProvider):
    """Mock datetime provider for testing."""
    
    def __init__(self, initial_datetime: datetime = None):
        self._current_datetime = initial_datetime or datetime(2024, 1, 15, 12, 0, 0)
    
    def now(self) -> datetime:
        return self._current_datetime
    
    def set_datetime(self, dt: datetime):
        """Set the current datetime."""
        self._current_datetime = dt


@pytest.fixture
def mock_time_provider() -> MockTimeProvider:
    """Fixture providing a mock time provider."""
    return MockTimeProvider()


@pytest.fixture
def mock_datetime_provider() -> MockDatetimeProvider:
    """Fixture providing a mock datetime provider."""
    return MockDatetimeProvider()


@pytest.fixture
def mock_http_session() -> Mock:
    """Fixture providing a mock HTTP session."""
    return Mock()


@pytest.fixture
def sample_match_data() -> dict:
    """Fixture providing sample match data from API."""
    return {
        "id": 123456,
        "utcDate": "2024-01-15T15:30:00Z",
        "status": "FINISHED",
        "homeTeam": {
            "name": "Arsenal FC",
            "shortName": "Arsenal",
            "tla": "ARS",
            "id": 674
        },
        "awayTeam": {
            "name": "Chelsea FC",
            "shortName": "Chelsea",
            "tla": "CHE",
            "id": 3929
        },
        "score": {
            "fullTime": {
                "home": 2,
                "away": 1
            },
        "winner": "HOME_TEAM"
        },
        "competition": {
            "id": 2001,
            "name": "Premier League",
            "code": "PL"
        }
    }


@pytest.fixture
def sample_api_response(sample_match_data) -> dict:
    """Fixture providing sample API response."""
    return {
        "matches": [sample_match_data]
    }


@pytest.fixture
def api_token() -> str:
    """Fixture providing a test API token."""
    return "test_api_token_12345"

