from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List
import os
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session

from app.services.football_api import FootballAPIClient
from app.dependencies import get_football_api_client
from app.database import SessionLocal, Base, engine
from app.models import Match as MatchModel
from app.schemas import MatchSchema, TeamSchema, CompetitionSchema, ScoreSchema


def get_db():
    """Dependency that provides a SQLAlchemy session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app):
    # Only create DB schema in non-production environments
    if os.getenv("ENV") != "production":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Soccer Match Tracker API",
    description="API for tracking soccer matches and highlights",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Soccer Match Tracker API",
        "version": "1.0.0",
        "endpoints": {
            "/health": "Health check",
            "/api/test-fetch": "Test fetching matches from Football Data API",
            "/api/matches": "Fetch matches (query params: competition, date_from, date_to)"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/test-fetch")
async def test_fetch(
    client: FootballAPIClient = Depends(get_football_api_client)
):
    """
    Test endpoint to fetch matches from Football Data API.
    Fetches matches from Premier League for the last 7 days.
    """
    try:
        # Fetch matches from Premier League for the last 7 days
        date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_to = datetime.now().strftime("%Y-%m-%d")
        
        print(f"\n{'='*60}")
        print("Testing Football Data API connection...")
        print(f"Date range: {date_from} to {date_to}")
        print(f"{'='*60}\n")
        
        processed_matches, raw_matches = client.get_matches(
            competition="premier league",
            date_from=date_from,
            date_to=date_to
        )
        
        print(f"\n{'='*60}")
        print(f"Successfully fetched {len(processed_matches)} matches")
        print(f"{'='*60}\n")
        
        # Print first few matches to console
        for i, match in enumerate(processed_matches[:5], 1):
            print(f"Match {i}:")
            print(f"  {match.home_team.name} vs {match.away_team.name}")
            print(f"  Score: {match.score.fullTime.home} - {match.score.fullTime.away}")
            print(f"  Date: {match.utc_date}")
            print(f"  Competition: {match.competition.name}")
            print()
        
        if len(processed_matches) > 5:
            print(f"... and {len(processed_matches) - 5} more matches\n")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Successfully fetched {len(processed_matches)} matches",
            "matches_count": len(processed_matches),
            "date_range": {
                "from": date_from,
                "to": date_to
            },
        })
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in test_fetch: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching matches: {str(e)}")


@app.get("/matches", response_model=List[MatchSchema])
def read_matches(db: Session = Depends(get_db)):
    """Return all matches persisted in the local database.

    Uses Pydantic `from_attributes` (ORM) mode to construct `MatchSchema`
    directly from SQLAlchemy model instances via `model_validate`.
    """
    try:
        db_matches = db.query(MatchModel).all()
        matches = [MatchSchema.model_validate(m) for m in db_matches]
        print(f"Fetched {len(matches)} matches from DB")
        return matches
    except Exception as e:
        print(f"Error reading matches from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
