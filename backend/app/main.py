from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, cast
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from sqlalchemy import literal

from app.services.sync_service import get_sync_freshness, update_sync_metadata, get_last_sync_time
from app.database import SessionLocal
from app.models import Match as MatchModel, User as UserModel, UserMatch as UserMatchModel
from app.scripts.sync_db import perform_sync
from app.schemas import (
    MatchSchema,
    UserCreate,
    UserResponse,
    UserMatchResponse,
)
from sqlalchemy.exc import IntegrityError

def get_db():
    """Dependency that provides a SQLAlchemy session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app):
    yield


app = FastAPI(
    title="Soccer Match Tracker API",
    description="API for tracking soccer matches and highlights",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/matches", response_model=List[MatchSchema])
def read_matches(email: str | None = None, 
                hide_done: bool = False, 
                limit: int = 20, 
                offset: int = 0, 
                db: Session = Depends(get_db)
    ):
    """
    Return all matches persisted in the local database.
    Fetch all matches and check if they are 'done' for a specific user using a single efficient SQL JOIN.
    """
    try:
        user_id: int | None = None
        if email:
            user = db.query(UserModel).filter(UserModel.email == email).first()
            if user:
                user_id = cast(int, user.id)
        
        query = db.query(MatchModel, UserMatchModel.is_done)
        
        if user_id:
            query = query.outerjoin(UserMatchModel, 
                                    (MatchModel.id == UserMatchModel.match_id) & 
                                    (UserMatchModel.user_id == user_id)
            )
        else:
            query = query.outerjoin(UserMatchModel, literal(False))

        if hide_done and user_id:
            query = query.filter(
                (UserMatchModel.is_done == False) | (UserMatchModel.is_done == None)
            )

        query = query.order_by(MatchModel.utc_date.desc()).offset(offset).limit(limit)

        results = []
        for match_obj, is_done_flag in query.all():
            schema_data = MatchSchema.model_validate(match_obj)
            schema_data.is_done = bool(is_done_flag)
            results.append(schema_data)

        return results
    except Exception as e:
        print(f"Error reading matches from DB: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Password is stored as a simple hash placeholder."""
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = f"hashed_{user.password}"
    u = UserModel(email=user.email, hashed_password=hashed)
    db.add(u)
    try:
        db.commit()
        db.refresh(u)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    return UserResponse.model_validate(u)



is_syncing_globally = False

@app.post("/api/matches/sync")
def trigger_sync(db: Session = Depends(get_db)):
    """
    Manually triggers a sync with the Football API to update local matches.
    """
    global is_syncing_globally
    if is_syncing_globally:
        raise HTTPException(status_code=429, detail="Sync already in progress. Please wait.")
    
    try:
        is_syncing_globally = True
        if get_sync_freshness(db, "matches_sync"):
            return {"success": True, "message": "Data is already fresh."}
        perform_sync(db)
        update_sync_metadata(db, "matches_sync", status="SUCCESS")
        return {"success": True, "message": "Database synced successfully"}
    
    except Exception as e:
        db.rollback()
        update_sync_metadata(db, "matches_sync", status="FAILED", error=str(e))
        print(f"Manual sync failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to sync with Football API. Check server logs.")
    
    finally:
        is_syncing_globally = False

@app.get("/api/matches/sync/status")
def get_sync_status(db: Session = Depends(get_db)):
    last_sync = get_last_sync_time(db, "matches_sync")
    return {
        "last_run_at": last_sync,
        "is_fresh": get_sync_freshness(db, "matches_sync")
    }

@app.get("/users/me", response_model=UserResponse)
def read_user_me(email: str, db: Session = Depends(get_db)):
    """
    Fetch the current user's profile. Frontend uses this to verify if the saved email is still valid.
    """
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User not found. Please log in again."
        )
    return user

@app.delete("/users/me")
def delete_user(email: str, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user) # Delete user will cascade to UserMatchModel due to foreign key constraints
    db.commit()
    return {"message": "Account deleted successfully"}

@app.post("/matches/{match_id}/status", response_model=UserMatchResponse)
def toggle_match_done(match_id: int, email: str, is_done: bool, db: Session = Depends(get_db)):
    """Mark a match as done for a given user. `match_id` is the external_id."""
    match = db.query(MatchModel).filter(MatchModel.external_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    # ensure user exists
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_match = db.query(UserMatchModel).filter(UserMatchModel.user_id == user.id, UserMatchModel.match_id == match.id).first()
    if user_match:
           user_match.is_done = is_done
    else:
        user_match = UserMatchModel(user_id=user.id, match_id=match.id, is_done=True)
        db.add(user_match)

    db.commit()
    return UserMatchResponse(user_id=cast(int, user.id), match_id=match_id, is_done=True)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
