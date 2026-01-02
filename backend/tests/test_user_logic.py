import pytest
from fastapi.testclient import TestClient

from app.main import app, get_db
from app.schemas import UserResponse, UserMatchResponse, UserCreate


def test_create_user_success(db_session, user_payload):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as client:
            payload = user_payload()
            res = client.post("/users", json=payload)
            assert res.status_code == 200
            body = res.json()
            user = UserResponse.model_validate(body)
            assert user.id
            assert user.email == payload["email"]
            # password must not be returned
            assert "password" not in body
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_create_user_duplicate_email(db_session, user_payload):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as client:
            payload = user_payload(email="dup@example.com")
            r1 = client.post("/users", json=payload)
            assert r1.status_code == 200
            r2 = client.post("/users", json=payload)
            assert r2.status_code == 400
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_mark_match_done_success(db_session, persisted_match, user_payload):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as client:
            # create user
            payload = user_payload(email="marker@example.com")
            r = client.post("/users", json=payload)
            assert r.status_code == 200
            user = UserResponse.model_validate(r.json())

            # mark match done
            res = client.post(f"/matches/{persisted_match.external_id}/done", params={"user_id": user.id})
            assert res.status_code == 200
            body = res.json()
            um = UserMatchResponse.model_validate(body)
            assert um.user_id == user.id
            assert um.match_id == persisted_match.external_id
            assert um.is_done is True
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_mark_match_done_missing_match(db_session, user_payload):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as client:
            # create user
            payload = user_payload(email="nomatch@example.com")
            r = client.post("/users", json=payload)
            assert r.status_code == 200
            user = UserResponse.model_validate(r.json())

            # try to mark non-existent match
            res = client.post("/matches/999999/done", params={"user_id": user.id})
            assert res.status_code == 404
    finally:
        app.dependency_overrides.pop(get_db, None)


def test_mark_match_done_missing_user(db_session, persisted_match):
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as client:
            # use a user id that doesn't exist
            res = client.post(f"/matches/{persisted_match.external_id}/done", params={"user_id": 999999})
            assert res.status_code == 404
    finally:
        app.dependency_overrides.pop(get_db, None)
