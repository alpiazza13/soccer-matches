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


def test_mark_match_done_success(client_with_db, persisted_match, user_payload):
        # create user
        payload = user_payload(email="marker@example.com")
        r = client_with_db.post("/users", json=payload)
        assert r.status_code == 200
        user = UserResponse.model_validate(r.json())

        # mark match done
        res = client_with_db.post(f"/matches/{persisted_match.external_id}/done", params={"user_id": user.id})
        assert res.status_code == 200
        body = res.json()
        um = UserMatchResponse.model_validate(body)
        assert um.user_id == user.id
        assert um.match_id == persisted_match.external_id
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
