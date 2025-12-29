"""
Dependency injection functions for FastAPI endpoints.
"""
import os
from functools import lru_cache
from dotenv import load_dotenv

from app.services.football_api import FootballAPIClient

load_dotenv()


@lru_cache()
def get_football_api_client() -> FootballAPIClient:
    """
    Dependency function to get FootballAPIClient instance.
    Uses lru_cache to ensure singleton pattern.
    """
    return FootballAPIClient()

