import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from main import app  # Import FastAPI app
from utility import hash_password, random_username, generate_temp_password, generate_unique_referral_code
from database import connect

client = TestClient(app)  # Create a synchronous test client

@pytest.fixture
def test_db():
    """Fixture to provide a test database session."""
    cur, conn = connect()
    yield cur, conn
    conn.rollback()  # Clean up after each test


###  Login Tests

def test_login_success(test_db):
    cur, conn = test_db
    new_user = random_username()
    new_email = new_user + "@testing.com"
    new_password = generate_temp_password()
    new_referral = generate_unique_referral_code(cur=cur, conn=conn)

    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                    (new_user, new_email, hash_password(new_password), new_referral, None))
    conn.commit()

    response = client.post("/api/login", data={
        "username": new_user,
        "password": new_password
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password(test_db):
    cur, conn = test_db
    new_user = random_username()
    new_email = new_user + "@testing.com"
    new_password = generate_temp_password()
    new_referral = generate_unique_referral_code(cur=cur, conn=conn)

    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                    (new_user, new_email, hash_password(new_password), new_referral, None))
    conn.commit()
    response = client.post("/api/login", data={
        "username": new_user,
        "password": "WrongPass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid credentials"