import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from utility import generate_unique_referral_code
from database import connect

def test_generate_unique_referral_code():
    cur, conn = connect()  # Get DB connection
    referral_code = generate_unique_referral_code(cur=cur, conn=conn)
    
    assert isinstance(referral_code, str)
    assert len(referral_code) == 8  # Ensuring correct length

def test_duplicate_referral_code():
    cur, conn = connect()  # Get DB connection
    first_code = generate_unique_referral_code(cur=cur, conn=conn)
    second_code = generate_unique_referral_code(cur=cur, conn=conn)
    
    assert first_code != second_code  # Ensure uniqueness
