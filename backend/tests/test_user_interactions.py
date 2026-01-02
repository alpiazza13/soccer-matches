import pytest
from app.models import User, Match, UserMatch, Team, Competition
from datetime import datetime, timezone

def test_user_mark_match_as_done(db_session):
    # 1. Setup: Create a Competition and Teams first (Required for Match FKs)
    comp = Competition(external_id=2021, name="Premier League", code="PL")
    team_h = Team(external_id=64, name="Liverpool FC", short_name="Liverpool", tla="LIV")
    team_a = Team(external_id=65, name="Manchester City", short_name="Man City", tla="MCI")
    
    db_session.add_all([comp, team_h, team_a])
    db_session.flush() # Get IDs without committing

    # 2. Setup: Create a Match
    match = Match(
        external_id=12345,
        utc_date=datetime.now(timezone.utc),
        status="FINISHED",
        competition_id=comp.id,
        home_team_id=team_h.id,
        away_team_id=team_a.id,
        score={"fullTime": {"home": 2, "away": 2}}
    )
    
    # 3. Setup: Create a User
    user = User(
        email="test@example.com",
        hashed_password="fakehashedpassword"
    )
    
    db_session.add_all([match, user])
    db_session.commit()

    # 4. Act: Link the user to the match as 'done'
    user_match = UserMatch(
        user_id=user.id,
        match_id=match.id,
        is_done=True,
        notes="What a game!"
    )
    db_session.add(user_match)
    db_session.commit()

    # 5. Assert: Verify the relationship works bidirectionally
    # Check from User side
    assert len(user.user_matches) == 1
    assert user.user_matches[0].match.external_id == 12345
    assert user.user_matches[0].is_done is True
    
    # Check from Match side
    assert len(match.user_matches) == 1
    assert match.user_matches[0].user.email == "test@example.com"