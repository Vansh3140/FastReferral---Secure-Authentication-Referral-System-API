import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
from fastapi.testclient import TestClient
from main import app  # Import FastAPI app
from database import connect
from utility import random_username, generate_temp_password, generate_unique_referral_code

client = TestClient(app)  # Create a synchronous test client

@pytest.fixture
def test_db():
    """Fixture to provide a test database session."""
    cur, conn = connect()
    yield cur, conn
    conn.rollback()  # Clean up after each test

### Registration Tests

def test_register_success():
    new_user = random_username()
    new_email = new_user + "@example.com"
    new_password = generate_temp_password()

    response = client.post("/api/register", json={
        "username": new_user,
        "email": new_email,
        "password": new_password
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully!"

def test_register_existing_email(test_db):
    cur, conn = test_db
    new_user = random_username()
    new_email = new_user + "@example.com"
    new_password = generate_temp_password()
    new_referral_code = generate_unique_referral_code(cur=cur, conn=conn)
    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                (new_user, new_email, new_password, new_referral_code, None))
    conn.commit()

    response = client.post("/api/register", json={
        "username": random_username(),
        "email": new_email,
        "password": "NewPass@123"
    })
    assert response.status_code == 400
    assert "Email already registered." in response.json()["detail"]

def test_register_existing_username(test_db):
    cur, conn = test_db
    new_user = random_username()
    new_email = new_user + "@example.com"
    new_password = generate_temp_password()
    new_referral_code = generate_unique_referral_code(cur=cur, conn=conn)
    cur.execute("INSERT INTO Users (username, email, password_hash, referral_code, referred_by) VALUES (%s, %s, %s, %s, %s)",
                (new_user, new_email, new_password, new_referral_code, None))
    conn.commit()

    response = client.post("/api/register", json={
        "username": new_user,
        "email": random_username() + "@example.com",
        "password": "NewPass@123"
    })
    assert response.status_code == 400
    assert "Username already taken." in response.json()["detail"]

def test_register_invalid_data():
    response = client.post("/api/register", json={})
    assert response.status_code == 422  # Validation error