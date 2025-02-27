import sys
import os

# Get the absolute path of the project's root directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from database import connect

def test_database_connection():
    cur, conn = connect()
    assert cur is not None
    assert conn is not None
    cur.close()
    conn.close()
