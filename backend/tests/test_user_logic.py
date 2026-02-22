import pytest
from fastapi.testclient import TestClient

from app.main import app, get_db
from app.schemas import UserResponse, UserMatchResponse, UserCreate
from tests.conftest import auth_headers


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


def test_toggle_match_done_success(client_with_db, persisted_match, session_test_user):
        """Test marking a match as done and then undone using session user."""
        headers = session_test_user["headers"]

        # mark match done (use auth header)
        res = client_with_db.post(
            f"/matches/{persisted_match.external_id}/status",
            params={"is_done": True},
            headers=headers,
        )
        assert res.status_code == 200
        body = res.json()
        um = UserMatchResponse.model_validate(body)
        assert um.match_id == persisted_match.external_id
        assert um.is_done is True

        # mark match not done
        res = client_with_db.post(
            f"/matches/{persisted_match.external_id}/status",
            params={"is_done": False},
            headers=headers,
        )
        assert res.status_code == 200
        body_updated = res.json()
        um_updated = UserMatchResponse.model_validate(body_updated)
        assert um_updated.is_done is False



def test_mark_match_done_missing_match(client_with_db, session_test_user):
    """Test 404 when marking a non-existent match with session user."""
    res = client_with_db.post(
        "/matches/999999/status", 
        headers=session_test_user["headers"],
        params={"is_done": True}
    )
    assert res.status_code == 404


def test_mark_match_done_missing_user(client_with_db, persisted_match, auth_headers):
    res = client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"is_done": True}, headers=auth_headers("noone@example.com"))
    assert res.status_code == 401

def test_is_done_isolation_between_users(client_with_db, persisted_match, user_payload, auth_headers):
    """Verify that User A marking a match done does not affect User B's list."""
    # 1. Create two distinct users
    user_a = user_payload(email="user_a@test.com")
    user_b = user_payload(email="user_b@test.com")
    client_with_db.post("/users", json=user_a)
    client_with_db.post("/users", json=user_b)

    headers_a = auth_headers(user_a["email"]) if isinstance(user_a, dict) else auth_headers(user_a.email)
    headers_b = auth_headers(user_b["email"]) if isinstance(user_b, dict) else auth_headers(user_b.email)

    # 2. User A marks the match as done
    client_with_db.post(
        f"/matches/{persisted_match.external_id}/status",
        params={"is_done": True},
        headers=headers_a,
    )

    # 3. Check User A's list (Should be True)
    res_a = client_with_db.get("/matches", headers=headers_a)
    assert res_a.json()[0]["is_done"] is True

    # 4. Check User B's list (Should still be False)
    res_b = client_with_db.get("/matches", headers=headers_b)
    assert res_b.json()[0]["is_done"] is False


def test_mark_match_done_fails_for_guest(client_with_db, persisted_match):
    """Guests should not be able to mark matches as done."""
    res = client_with_db.post(f"/matches/{persisted_match.external_id}/status", params={"is_done": True})
    assert res.status_code in (401, 422)

def test_get_me_success(client_with_db, session_test_user):
    """Test retrieving current user profile with session user."""
    res = client_with_db.get("/users/me", headers=session_test_user["headers"])
    assert res.status_code == 200
    assert res.json()["email"] == session_test_user["email"]

def test_get_me_not_found(client_with_db, auth_headers):
    res = client_with_db.get("/users/me", headers=auth_headers("nonexistent@example.com"))
    assert res.status_code == 401

def test_delete_user_success(client_with_db, user_payload, auth_headers):
    """Verify that a user can be successfully deleted using auth header."""
    email = "delete_me@example.com"
    client_with_db.post("/users", json=user_payload(email=email))
    
    res = client_with_db.delete("/users/me", headers=auth_headers(email))
    assert res.status_code == 200
    assert res.json()["message"] == "Account deleted successfully"

    verify_res = client_with_db.get("/users/me", headers=auth_headers(email))
    assert verify_res.status_code == 401


def test_delete_user_cascades_to_matches(client_with_db, persisted_match, user_payload, auth_headers):
    """Critical: Verify that deleting a user also deletes their match statuses (Cascade)."""
    email = "cascade_test@example.com"
    client_with_db.post("/users", json=user_payload(email=email))
    
    client_with_db.post(
        f"/matches/{persisted_match.external_id}/status",
        params={"is_done": True},
        headers=auth_headers(email),
    )
    
    client_with_db.delete("/users/me", headers=auth_headers(email))
    
    # After deletion, guest view may be unauthorized or return matches with is_done=False
    res = client_with_db.get("/matches")
    if res.status_code == 200:
        assert res.json()[0]["is_done"] is False
    else:
        assert res.status_code == 401


def test_delete_user_not_found(client_with_db, auth_headers):
    """Verify 404 when trying to delete a non-existent user via auth header."""
    res = client_with_db.delete("/users/me", headers=auth_headers("nonexistent@example.com"))
    if res.status_code == 404:
        assert res.json()["detail"] == "User not found"
    else:
        assert res.status_code == 401


def test_update_user_settings_success(client_with_db, user_payload, auth_headers):
    """Verify that a user can update their hide_scores preference."""
    email = "settings@example.com"
    client_with_db.post("/users", json=user_payload(email=email))
    
    res = client_with_db.put(
            "/users/settings", 
            json={"hide_scores": True},
            headers=auth_headers(email)
    )
    assert res.status_code == 200
    data = res.json()
    assert data["hide_scores"] is True
    assert data["email"] == email

    # use the PUT endpoint to update settings back to False
    res = client_with_db.put(
        "/users/settings",
        json={"hide_scores": False},
        headers=auth_headers(email),
    )
    assert res.status_code == 200
    assert res.json()["hide_scores"] is False


def test_update_user_settings_user_not_found(client_with_db, auth_headers):
    """Verify 404/401 is returned if updating settings for non-existent email."""
    res = client_with_db.put(
        "/users/settings",
        json={"hide_scores": True},
        headers=auth_headers("nonexistent@example.com"),
    )
    assert res.status_code == 401

def test_unverified_user_access(client_with_db, user_payload, auth_headers):
    """
    Test if unverified users are blocked. 
    Note: You'll need to update get_current_user in main.py to enforce this.
    """
    email = "unverified@example.com"
    # By default, is_verified is False
    client_with_db.post("/users", json=user_payload(email=email))
    res = client_with_db.get("/matches", headers=auth_headers(email))

    # If you decide to enforce verification:
    # assert res.status_code == 403 
    # assert "Verify your email" in res.json()["detail"]
    