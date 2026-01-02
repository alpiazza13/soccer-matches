import pytest
from app.models import User, UserMatch


def test_user_mark_match_as_done(db_session, persisted_match):
    # persisted_match fixture provides Team, Competition and Match rows
    user = User(email="test@example.com", hashed_password="fakehashedpassword")
    db_session.add(user)
    db_session.commit()

    user_match = UserMatch(user_id=user.id, match_id=persisted_match.id, is_done=True, notes="What a game!")
    db_session.add(user_match)
    db_session.commit()

    # Refresh instances to ensure relationships are populated
    db_session.refresh(user)
    db_session.refresh(persisted_match)

    # Assert relationships
    assert len(user.user_matches) == 1
    assert user.user_matches[0].match.external_id == persisted_match.external_id
    assert user.user_matches[0].is_done is True

    assert len(persisted_match.user_matches) == 1
    assert persisted_match.user_matches[0].user.email == "test@example.com"