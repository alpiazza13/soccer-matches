# Soccer Match Tracker - Backend

FastAPI backend for the Soccer Match Tracker application.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

4. Add your Football Data API token to `.env`:
```
FOOTBALL_DATA_API_TOKEN=your_actual_token_here
```

## Running the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /` - Root endpoint with API information
- `GET /health` - Health check
- `GET /api/test-fetch` - Test endpoint to fetch matches from Premier League (last 7 days)
- `GET /api/matches` - Fetch matches with optional query parameters:
  - `competition` - Competition name (e.g., 'premier league', 'serie a')
  - `date_from` - Start date (YYYY-MM-DD)
  - `date_to` - End date (YYYY-MM-DD)

## Example Requests

Test fetch:
```bash
curl http://localhost:8000/api/test-fetch
```

Get matches from Premier League:
```bash
curl "http://localhost:8000/api/matches?competition=premier%20league"
```

Get matches from all competitions:
```bash
curl http://localhost:8000/api/matches
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

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

See `tests/README.md` for more testing information.

