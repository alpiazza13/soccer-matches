import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from http.client import responses

from app.utils.time_provider import TimeProvider, SystemTimeProvider, DatetimeProvider, SystemDatetimeProvider
from app.schemas import MatchSchema, TeamSchema, CompetitionSchema


class FootballAPIClient:
    """
    Client for interacting with the Football Data API v4.
    Handles rate limiting (10 calls per minute) and match data fetching.
    """
    
    BASE_URL = "https://api.football-data.org/v4"
    
    # Competition IDs mapping
    COMPETITION_IDS = {
        'serie a': 2019,
        'premier league': 2021,
        'champions league': 2001,
        'ligue 1': 2015,
        'bundesliga': 2002,
        'spanish league': 2014,
        'world cup': 2000,
        'euros': 2018
    }
    
    def __init__(
        self, 
        api_token: str | None = None,
        http_session: requests.Session | None = None,
        time_provider: TimeProvider | None = None,
        datetime_provider: DatetimeProvider | None = None
    ):
        """
        Initialize the Football API client.
        
        Args:
            api_token: API token for Football Data API. If not provided, 
                      will try to get from FOOTBALL_DATA_API_TOKEN env var.
            http_session: HTTP session for making requests. If not provided,
                         uses requests module directly (for backward compatibility).
            time_provider: Provider for time operations. If not provided,
                          uses SystemTimeProvider.
            datetime_provider: Provider for datetime operations. If not provided,
                              uses SystemDatetimeProvider.
        """
        self.api_token = api_token or os.getenv("FOOTBALL_DATA_API_TOKEN")
        if not self.api_token:
            raise ValueError("API token is required. Set FOOTBALL_DATA_API_TOKEN environment variable.")
        
        self.headers = {"X-Auth-Token": self.api_token}
        self.last_request_time = 0
        self.min_request_interval = 6.0  # 10 calls per minute = 6 seconds between calls
        
        # Dependency injection for testability
        self.http_session = http_session
        self._time_provider = time_provider or SystemTimeProvider()
        self._datetime_provider = datetime_provider or SystemDatetimeProvider()
    
    def _rate_limit(self):
        """Ensure we don't exceed 10 calls per minute."""
        current_time = self._time_provider.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            self._time_provider.sleep(sleep_time)
        
        self.last_request_time = self._time_provider.time()
    
    def _make_request(self, url: str, params: Dict[str, str]) -> requests.Response:
        """
        Make HTTP request using the configured session or requests module.
        
        Args:
            url: Request URL
            params: Query parameters
        
        Returns:
            Response object
        """
        if self.http_session:
            return self.http_session.get(url, headers=self.headers, params=params)
        else:
            return requests.get(url, headers=self.headers, params=params)
    
    def get_matches(
        self, 
        competition: str, 
        date_from: str | None = None, 
        date_to: str | None = None
    ) -> Tuple[List[MatchSchema], List[Dict]]:
        """
        Fetch matches for a given competition within a date range.
        
        Args:
            competition: Competition name (e.g., 'premier league', 'serie a')
            date_from: Start date in YYYY-MM-DD format. If None, fetches from last 7 days.
            date_to: End date in YYYY-MM-DD format. If None, uses today.
        
        Returns:
            Tuple of (processed_matches, raw_matches):
            - processed_matches: List of dicts with extracted match data
            - raw_matches: List of dicts with full API response data
        """
        if competition.lower() not in self.COMPETITION_IDS:
            raise ValueError(
                f"Unknown competition: {competition}. "
                f"Available: {list(self.COMPETITION_IDS.keys())}"
            )
        
        competition_id = self.COMPETITION_IDS[competition.lower()]
        
        # Set default date range if not provided
        if date_to is None:
            date_to = self._datetime_provider.now().strftime("%Y-%m-%d")
        if date_from is None:
            date_from = (self._datetime_provider.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        # Apply rate limiting
        self._rate_limit()
        
        # Build API URL
        url = f"{self.BASE_URL}/competitions/{competition_id}/matches"
        params = {
            "dateFrom": date_from,
            "dateTo": date_to
        }
        
        # Make API request
        response = self._make_request(url, params)
        status_code = response.status_code
        
        print(f"\nFetching matches from {competition}")
        print(f"API Response: status code {status_code}, {responses.get(status_code, 'Unknown')}")
        
        if status_code != 200:
            response.raise_for_status()
        
        matches = response.json().get('matches', [])
        print(f"Found {len(matches)} matches")
        
        # Process matches
        processed_matches = []
        raw_matches = []
        
        for match in matches:
            # Extract match information
            match_info = self._extract_match_info(match)
            processed_matches.append(match_info)
            
            # Store raw data
            raw_match = {
                "id": match["id"],
                "all_match_data": match
            }
            raw_matches.append(raw_match)
        
        return processed_matches, raw_matches
    
    def _extract_match_info(self, raw_data: Dict) -> MatchSchema:
        """
        Extract relevant information from a match API response.
        
        Args:
            match: Raw match data from API
            competition: Competition name
        
        Returns:
            Dictionary with extracted match information
        """
        home = TeamSchema(
                id=raw_data["homeTeam"]["id"],
                name=raw_data["homeTeam"]["name"],
                short_name=raw_data["homeTeam"].get("shortName"),
                tla=raw_data["homeTeam"].get("tla")
            )
        away = TeamSchema(
            id=raw_data["awayTeam"]["id"],
            name=raw_data["awayTeam"]["name"],
            short_name=raw_data["awayTeam"].get("shortName"),
            tla=raw_data["awayTeam"].get("tla")
        )
        
        # 2. Clean the competition
        comp = CompetitionSchema(
            id=raw_data["competition"]["id"],
            name=raw_data["competition"]["name"],
            code=raw_data["competition"]["code"]
        )

        # 3. Return the validated MatchSchema
        return MatchSchema(
            match_id=raw_data["id"],
            status=raw_data["status"],
            utc_date=datetime.fromisoformat(raw_data["utcDate"].replace('Z', '+00:00')),
            home_team=home,
            away_team=away,
            competition=comp,
            score=raw_data["score"]
        )

    
    def fetch_all_matches(
        self, 
        date_from: str | None = None, 
        date_to: str | None = None
    ) -> Tuple[List[MatchSchema], List[Dict]]:
        """
        Fetch matches from all supported competitions.
        
        Args:
            date_from: Start date in YYYY-MM-DD format
            date_to: End date in YYYY-MM-DD format
        
        Returns:
            Tuple of (all_processed_matches, all_raw_matches)
        """
        all_processed_matches = []
        all_raw_matches = []
        
        for competition in self.COMPETITION_IDS.keys():
            try:
                processed, raw = self.get_matches(competition, date_from, date_to)
                all_processed_matches.extend(processed)
                all_raw_matches.extend(raw)
            except Exception as e:
                print(f"Error fetching {competition}: {e}")
                continue
        
        return all_processed_matches, all_raw_matches
