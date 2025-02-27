import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utility import (
    send_password, 
    generate_temp_password,
    get_password_strength,
    hash_password,
    verify_password
    )
import re
from dotenv import load_dotenv
import os

load_dotenv()

def test_generate_temp_password():
    password1 = generate_temp_password()
    password2 = generate_temp_password()
    
    # Check password length (e.g., should be at least 8 characters)
    assert len(password1) >= 8
    assert len(password2) >= 8

    # Ensure randomness
    assert password1 != password2  

    # Verify it contains uppercase, lowercase, digits, and special characters
    assert re.search(r'[A-Z]', password1)  # At least one uppercase letter
    assert re.search(r'[a-z]', password1)  # At least one lowercase letter
    assert re.search(r'\d', password1)     # At least one digit
    assert re.search(r'[!@#$%^&*(),.?":{}|<>]', password1)  # At least one special character



def test_get_password_strength():
    # Too Short (Weak)
    assert get_password_strength("123") == ("Weak", False)
    assert get_password_strength("aB1") == ("Weak", False)
    
    # Moderate (Length < 8 but has letters and numbers)
    assert get_password_strength("abc123") == ("Moderate", False)
    assert get_password_strength("A1b2C3") == ("Moderate", False)

    # Strong (>= 8, has upper, lower, digit)
    assert get_password_strength("Password1") == ("Strong", True)
    assert get_password_strength("Testing123") == ("Strong", True)

    # Very Strong (>= 8, has upper, lower, digit, special character)
    assert get_password_strength("Str0ng@Pass") == ("Very Strong", True)
    assert get_password_strength("My$ecureP@ss1") == ("Very Strong", True)

    # Edge Cases
    assert get_password_strength("onlylower") == ("Weak", False)  # No number, no uppercase
    assert get_password_strength("ONLYUPPER") == ("Weak", False)  # No number, no lowercase
    assert get_password_strength("123456789") == ("Weak", False)  # No letters


def test_hash_password():
    password = "SecurePass123"
    hashed_pw = hash_password(password)
    assert hashed_pw != password  # Password should be hashed


def test_verify_password():
    password = "SecurePass123"
    hashed_pw = hash_password(password)
    assert verify_password(password, hashed_pw)  # Should return True
    assert not verify_password("WrongPass", hashed_pw)  # Should return False

def test_send_password():
    # Replace with your real email
    test_email = os.getenv("TEST_EMAIL")

    # Run the function to send an actual email
    success = send_password("TestPass123", test_email, "TestUser")
    assert success