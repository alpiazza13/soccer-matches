import pytest

def test_login_success(client_with_db, user_payload):
    email = "login@example.com"
    password = "password123"
    client_with_db.post("/users", json=user_payload(email=email, password=password))

    # OAuth2 uses form data (username/password), not JSON
    response = client_with_db.post("/token", data={"username": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client_with_db, user_payload):
    client_with_db.post("/users", json=user_payload(email="test@example.com", password="real"))
    response = client_with_db.post("/token", data={"username": "test@example.com", "password": "wrong"})
    assert response.status_code == 401