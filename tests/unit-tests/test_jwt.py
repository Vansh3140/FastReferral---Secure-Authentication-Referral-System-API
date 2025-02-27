import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

import pytest
import jwt
from datetime import timedelta
from dotenv import load_dotenv
from utility import create_access_token

load_dotenv()

def test_create_access_token():
    data = {"sub": "testuser"}
    token = create_access_token(data, expires_delta=timedelta(minutes=1440))
    
    assert isinstance(token, str)

    decoded_data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    assert decoded_data["sub"] == "testuser"

def test_invalid_token():
    invalid_token = "invalid.jwt.token"
    with pytest.raises(jwt.exceptions.DecodeError):
        jwt.decode(invalid_token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
