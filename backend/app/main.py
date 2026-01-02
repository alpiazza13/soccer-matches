from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional

from app.services.football_api import FootballAPIClient
from app.dependencies import get_football_api_client

app = FastAPI(
    title="Soccer Match Tracker API",
    description="API for tracking soccer matches and highlights",
    version="1.0.0"
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


@app.get("/api/matches")
async def get_matches(
    competition: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    client: FootballAPIClient = Depends(get_football_api_client)
):
    """
    Fetch matches from Football Data API.
    
    Query Parameters:
        competition: Competition name (e.g., 'premier league', 'serie a'). 
                    If not provided, fetches from all competitions.
        date_from: Start date in YYYY-MM-DD format. Defaults to 7 days ago.
        date_to: End date in YYYY-MM-DD format. Defaults to today.
    """
    pass

    '''
    try:
        # Set default date range if not provided
        if date_to is None:
            date_to = datetime.now().strftime("%Y-%m-%d")
        if date_from is None:
            date_from = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        
        if competition:
            # Fetch from specific competition
            processed_matches, raw_matches = client.get_matches(
                competition=competition,
                date_from=date_from,
                date_to=date_to
            )
        else:
            # Fetch from all competitions
            processed_matches, raw_matches = client.fetch_all_matches(
                date_from=date_from,
                date_to=date_to
            )
        
        return JSONResponse(content={
            "success": True,
            "matches_count": len(processed_matches),
            "date_range": {
                "from": date_from,
                "to": date_to
            },
            "competition": competition or "all",
            "matches": processed_matches
        })
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error in get_matches: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching matches: {str(e)}")
    '''


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
