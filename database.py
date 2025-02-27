import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

def connect():

    conn = psycopg2.connect(os.getenv("DB_CONNECT"))

    query_sql = 'SELECT VERSION()'

    cur = conn.cursor()
    cur.execute(query_sql)

    version = cur.fetchone()[0]
    print(f"The Postgres Database is connected!! Version : {version}")
    return cur, conn

def main():
    cur, conn = connect()
    # create_tables(cur=cur, conn=conn)
    # print_table(cur, "Rewards")

def clear_all_data():
    """Clears all data from Users, Referrals, and Rewards tables."""
    cur, conn = connect()

    try:
        cur.execute("TRUNCATE TABLE Referrals, Rewards, Users RESTART IDENTITY CASCADE;")
        conn.commit()
        print("All tables cleared successfully!")
    
    except Exception as e:
        conn.rollback()
        print(f"Error clearing tables: {e}")

    finally:
        cur.close()
        conn.close()

def create_tables(cur, conn):
    # Users Table
    create_users_table = """
    CREATE TABLE IF NOT EXISTS Users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        referral_code VARCHAR(20) UNIQUE,
        referred_by VARCHAR(20),
        created_at TIMESTAMP DEFAULT NOW(),
        CONSTRAINT fk_referred_by FOREIGN KEY (referred_by) REFERENCES Users(referral_code)
    );
    """

    # Referrals Table
    create_referrals_table = """
    CREATE TABLE IF NOT EXISTS Referrals (
        id SERIAL PRIMARY KEY,
        referrer_id INT NOT NULL,
        referred_user_id INT NOT NULL,
        date_referred TIMESTAMP DEFAULT NOW(),
        status VARCHAR(20) CHECK (status IN ('pending', 'successful', 'failed')),
        FOREIGN KEY (referrer_id) REFERENCES Users(id) ON DELETE CASCADE,
        FOREIGN KEY (referred_user_id) REFERENCES Users(id) ON DELETE CASCADE
    );
    """

    # Rewards Table (Optional)
    create_rewards_table = """
    CREATE TABLE IF NOT EXISTS Rewards (
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL,
        reward_type VARCHAR(50),
        reward_amount DECIMAL(10,2),
        reward_status VARCHAR(20) CHECK (reward_status IN ('pending', 'claimed', 'expired')),
        created_at TIMESTAMP DEFAULT NOW(),
        FOREIGN KEY (user_id) REFERENCES Users(id) ON DELETE CASCADE
    );
    """

    # Execute table creation queries
    cur.execute(create_users_table)
    cur.execute(create_referrals_table)
    cur.execute(create_rewards_table)

    # Commit changes
    conn.commit()
    print("Users Table, Referrals Table, Rewards Table => created successfully!")

def print_table(cur, table_name):
    query = f"SELECT * FROM {table_name};"
    cur.execute(query)
    rows = cur.fetchall()

    if not rows:
        print(f"No data found in {table_name} table.")
        return

    # Print column names
    col_names = [desc[0] for desc in cur.description]
    print(" | ".join(col_names))
    print("-" * 80)

    # Print each row
    for row in rows:
        print(" | ".join(str(value) for value in row))

if __name__ == "__main__":
    main()