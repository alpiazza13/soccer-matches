import pytest

def test_login_success(client_with_db, session_test_user):
    """Test successful login with existing session user."""
    email = session_test_user["email"]
    password = session_test_user["password"]

    # OAuth2 uses form data (username/password), not JSON
    response = client_with_db.post("/token", data={"username": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client_with_db, session_test_user):
    """Test login failure with wrong password for existing session user."""
    response = client_with_db.post("/token", data={"username": session_test_user["email"], "password": "wrong"})
    assert response.status_code == 401