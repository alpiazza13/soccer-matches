import pytest
from fastapi.testclient import TestClient

from app.main import app, get_db
from app.schemas import UserResponse, UserMatchResponse, UserCreate


def test_create_user_success(client_with_db, user_payload):
        payload = user_payload()
        res = client_with_db.post("/users", json=payload)
        assert res.status_code == 200
        body = res.json()
        user = UserResponse.model_validate(body)
        assert user.id
        assert user.email == payload["email"]
        assert "password" not in body


def test_create_user_duplicate_email(client_with_db, user_payload):
        payload = user_payload(email="dup@example.com")
        r1 = client_with_db.post("/users", json=payload)
        assert r1.status_code == 200
        r2 = client_with_db.post("/users", json=payload)
        assert r2.status_code == 400


def test_toggle_match_done_success(client_with_db, persisted_match, user_payload):
        # create user
        payload = user_payload(email="marker@example.com")
        r = client_with_db.post("/users", json=payload)
        assert r.status_code == 200
        user = UserResponse.model_validate(r.json())

        # mark match done
        res = client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"user_id": user.id, "is_done": True})
        assert res.status_code == 200
        body = res.json()
        um = UserMatchResponse.model_validate(body)
        assert um.user_id == user.id
        assert um.match_id == persisted_match.external_id

        # mark match not done
        res = client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"user_id": user.id, "is_done": False})
        assert res.status_code == 200
        assert um.is_done is True



def test_mark_match_done_missing_match(client_with_db, user_payload):
        # create user
        payload = user_payload(email="nomatch@example.com")
        r = client_with_db.post("/users", json=payload)
        assert r.status_code == 200
        user = UserResponse.model_validate(r.json())

        # try to mark non-existent match
        res = client_with_db.post("/matches/999999/done", params={"user_id": user.id})
        assert res.status_code == 404


def test_mark_match_done_missing_user(client_with_db, persisted_match):
        # use a user id that doesn't exist
        res = client_with_db.post(f"/matches/{persisted_match.external_id}/done", params={"user_id": 99999})
        assert res.status_code == 404

def test_is_done_isolation_between_users(client_with_db, persisted_match, user_payload):
    """Verify that User A marking a match done does not affect User B's list."""
    # 1. Create two distinct users
    user_a_id = client_with_db.post("/users", json=user_payload(email="user_a@test.com")).json()["id"]
    user_b_id = client_with_db.post("/users", json=user_payload(email="user_b@test.com")).json()["id"]

    # 2. User A marks the match as done
    client_with_db.post(
        f"/matches/{persisted_match.external_id}/status", 
        params={"user_id": user_a_id, "is_done": True}
    )

    # 3. Check User A's list (Should be True)
    res_a = client_with_db.get("/matches", params={"user_id": user_a_id})
    assert res_a.json()[0]["is_done"] is True

    # 4. Check User B's list (Should still be False)
    res_b = client_with_db.get("/matches", params={"user_id": user_b_id})
    assert res_b.json()[0]["is_done"] is False


def test_mark_match_done_fails_for_guest(client_with_db, persisted_match):
    """Guests should not be able to mark matches as done."""
    res = client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"is_done": True})
    assert res.status_code == 422

def test_get_me_success(client_with_db, user_payload):
    payload = user_payload(email="me@example.com")
    create_res = client_with_db.post("/users", json=payload)
    user_id = create_res.json()["id"]

    res = client_with_db.get("/users/me", params={"user_id": user_id})
    assert res.status_code == 200
    assert res.json()["email"] == "me@example.com"

def test_get_me_not_found(client_with_db):
    res = client_with_db.get("/users/me", params={"user_id": 99999})
    assert res.status_code == 404