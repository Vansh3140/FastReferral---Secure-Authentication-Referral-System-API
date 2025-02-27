import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from main import app  # Import FastAPI app
from utility import hash_password, random_username, generate_unique_referral_code, generate_temp_password
from database import connect

client = TestClient(app)  # Create a synchronous test client

@pytest.fixture
def test_db():
    """Fixture to provide a test database session."""
    cur, conn = connect()
    yield cur, conn
    conn.rollback()  # Clean up after each test


### Referral System Tests

def test_successful_referral(test_db):
    cur, conn = test_db

    new_user = random_username()
    new_email = new_user + "@example.com"
    new_password = generate_temp_password()
    new_referral_code = generate_unique_referral_code(cur=cur, conn=conn)
    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                (new_user, new_email, hash_password(new_password), new_referral_code, None))
    conn.commit()

    response = client.post("/api/register", json={
        "username": random_username(),
        "email": random_username() + "@example.com",
        "password": generate_temp_password(),
        "referral_code": new_referral_code
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully!"

def test_invalid_referral_code():
    response = client.post("/api/register", json={
        "username": random_username(),
        "email": random_username() + "@example.com",
        "password": generate_temp_password(),
        "referral_code": "INVALID123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid Referral Code."

def test_user_cannot_refer_themselves(test_db):
    cur, conn = test_db

    new_user = random_username()
    new_email = new_user + "@example.com"
    new_password = generate_temp_password()
    new_referral_code = generate_unique_referral_code(cur=cur, conn=conn)
    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                (new_user, new_email, hash_password(new_password), new_referral_code, None))
    conn.commit()

    response = client.post("/api/register", json={
        "username": new_user,
        "email": new_email,
        "password": new_password,
        "referral_code": new_referral_code
    })
    assert response.status_code == 400

def test_referral_count_tracking(test_db):
    cur, conn = test_db

    # 1. Create the referrer user
    new_user = random_username()
    new_email = new_user + "@example.com"
    new_password = generate_temp_password()
    new_referral_code = generate_unique_referral_code(cur=cur, conn=conn)
    
    # Insert referrer with NULL for referred_by
    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                (new_user, new_email, hash_password(new_password), new_referral_code, None))
    conn.commit()
    
    # 2. Register two new users with the referral code
    client.post("/api/register", json={
        "username": random_username(),
        "email": random_username() + "@example.com",
        "password": generate_temp_password(),
        "referral_code": new_referral_code
    })
    client.post("/api/register", json={
        "username": random_username(),
        "email": random_username() + "@example.com",
        "password": generate_temp_password(),
        "referral_code": new_referral_code
    })
    
    # 3. Login as the referrer to get an access token
    login_response = client.post("/api/login", data={
        "username": new_user,
        "password": new_password
    })
    access_token = login_response.json()["access_token"]
    
    # 4. Get referral stats using the access token
    response = client.get(
        "/api/referral-stats",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # 5. Assert the response
    assert response.status_code == 200
    assert response.json()["successful_referrals"] == 2
