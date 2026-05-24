from typing import List, cast
from contextlib import asynccontextmanager

from sqlalchemy.orm import Session
from sqlalchemy import literal
from sqlalchemy.exc import IntegrityError

from mangum import Mangum

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


from app.services.sync_service import get_sync_freshness, update_sync_metadata, get_last_sync_time
from app.database import get_db
from app.models import Match as MatchModel, User as UserModel, UserMatch as UserMatchModel
from app.scripts.sync_db import perform_sync
from app.schemas import (
    MatchSchema,
    UserCreate,
    UserResponse,
    UserMatchResponse,
    UserSettingsUpdate,
)
from app.utils.security import hash_password, verify_password, create_access_token, get_current_user




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
    allow_origins=["http://localhost:3000", "https://main.d1hthutgtmryew.amplifyapp.com"],
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
def read_matches(
    hide_done: bool = False, 
    limit: int = 20, 
    offset: int = 0, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # Now required & secure
):
    """
    Return matches and check if they are 'done' for the logged-in user.
    """
    try:
        user_id = cast(int, current_user.id)
        query = db.query(MatchModel, UserMatchModel.is_done)
        
        query = query.outerjoin(UserMatchModel, 
                                (MatchModel.id == UserMatchModel.match_id) & 
                                (UserMatchModel.user_id == user_id)
        )

        if hide_done:
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
        raise HTTPException(status_code=500, detail="Internal server error")
    

@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user. Password is stored as a simple hash placeholder."""
    existing = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pwd = hash_password(user.password)
    new_user = UserModel(email=user.email, hashed_password=hashed_pwd, is_active=True)
    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email already registered")

    return new_user

@app.post("/token")
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Find user by email (OAuth2 uses 'username' field for the login ID)
    user = db.query(UserModel).filter(UserModel.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401, 
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(subject=user.email)
    return {"access_token": access_token, "token_type": "bearer"}

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
def read_user_me(current_user: UserModel = Depends(get_current_user)):
    """
    Fetch the current user's profile using their JWT token.
    """
    return current_user

@app.delete("/users/me")
def delete_user(
    db: Session = Depends(get_db), 
    current_user: UserModel = Depends(get_current_user)
):
    db.delete(current_user) 
    db.commit()
    return {"message": "Account deleted successfully"}

@app.put("/users/settings", response_model=UserResponse)
def update_user_settings(
    settings: UserSettingsUpdate, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Update user preferences like hide_scores securely."""
    current_user.hide_scores = settings.hide_scores
    
    db.commit()
    db.refresh(current_user)
    return current_user

@app.post("/matches/{match_id}/status", response_model=UserMatchResponse)
def toggle_match_done(
    match_id: int, 
    is_done: bool, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user) # Securely identified
):
    """Mark a match as done for a given user. `match_id` is the external_id."""
    match = db.query(MatchModel).filter(MatchModel.external_id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    user_match = db.query(UserMatchModel).filter(
        UserMatchModel.user_id == current_user.id, 
        UserMatchModel.match_id == match.id
    ).first()

    if user_match:
           user_match.is_done = is_done
    else:
        user_match = UserMatchModel(user_id=current_user.id, match_id=match.id, is_done=is_done)
        db.add(user_match)

    db.commit()
    return UserMatchResponse(user_id=cast(int, current_user.id), match_id=match_id, is_done=is_done)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    Overrides the default 422 error response to provide a 
    cleaner message for the frontend.
    """
    errors = exc.errors()
    if not errors:
        return JSONResponse(status_code=422, content={"detail": "Validation error"})

    # Grab the first error in the list
    first_error = errors[0]
    
    # field name is usually the last item in the 'loc' tuple (e.g., 'email' or 'password')
    field = str(first_error.get("loc", ["field"])[-1])
    msg = first_error.get("msg", "Invalid value")

    # Simplify common Pydantic messages
    if "value is not a valid email address" in msg:
        clean_message = "Please enter a valid email address."
    else:
        clean_message = f"Invalid {field}: {msg}"

    return JSONResponse(
        status_code=422,
        content={"detail": clean_message},
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

# Standardize the Mangum handler wrapper for AWS Lambda execution
handler = Mangum(app)