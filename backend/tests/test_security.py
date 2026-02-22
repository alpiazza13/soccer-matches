import pytest
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
from app.utils.security import (
    hash_password, 
    verify_password, 
    create_access_token, 
    SECRET_KEY, 
    ALGORITHM
)

# 1. Test Password Hashing
def test_hash_password_creates_secure_string():
    password = "my_secure_password"
    hashed = hash_password(password)
    
    assert hashed != password
    # Bcrypt hashes typically start with $2b$
    assert hashed.startswith("$2b$")

def test_verify_password_correct():
    password = "test_password"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    password = "test_password"
    hashed = hash_password(password)
    assert verify_password("wrong_password", hashed) is False

def test_salting_logic():
    # Even with the same password, hashes should be different due to random salt
    password = "same_password"
    hash1 = hash_password(password)
    hash2 = hash_password(password)
    assert hash1 != hash2


# 2. Test JWT Token Generation
def test_create_access_token_payload():
    email = "user@example.com"
    token = create_access_token(subject=email)
    
    # Decode the token and check the content
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload["sub"] == email
    # Ensure 'exp' (expiration) claim exists
    assert "exp" in payload

def test_create_access_token_custom_expiry():
    email = "user@example.com"
    expires_delta = timedelta(minutes=10)
    token = create_access_token(subject=email, expires_delta=expires_delta)
    
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    expiration = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    
    # The expiration should be roughly 10 minutes from now
    now = datetime.now(timezone.utc)
    diff = expiration - now
    assert 9 < diff.total_seconds() / 60 <= 10

def test_token_is_invalid_with_wrong_secret():
    email = "user@example.com"
    token = create_access_token(subject=email)
    
    with pytest.raises(JWTError):
        # Trying to decode with a different secret should fail
        jwt.decode(token, "wrong-secret-key", algorithms=[ALGORITHM])