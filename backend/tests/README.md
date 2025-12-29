# Tests

This directory contains unit and integration tests for the Soccer Match Tracker backend.

## Running Tests

Run all tests:
```bash
pytest
```

Run with verbose output:
```bash
pytest -v
```

Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

Run specific test file:
```bash
pytest tests/test_football_api.py
```

Run specific test:
```bash
pytest tests/test_football_api.py::TestFootballAPIClient::test_get_matches_success
```

## Test Structure

- `conftest.py` - Shared pytest fixtures
- `test_football_api.py` - Unit tests for FootballAPIClient
- `test_main.py` - Integration tests for FastAPI endpoints

## Test Coverage

The tests cover:
- FootballAPIClient initialization and configuration
- Match data fetching with various parameters
- Rate limiting behavior
- Error handling
- Date/time formatting
- API endpoint responses
- Dependency injection

