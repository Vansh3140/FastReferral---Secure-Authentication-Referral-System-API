from database import connect
from datetime import datetime, timedelta, timezone
import bcrypt
import re
import jwt
import os
from jwt.exceptions import InvalidTokenError
import string
import random
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    cur, conn = connect()
    try:
        yield cur, conn
    finally:
        cur.close()
        conn.close()

def send_password(password: str, email: str, user: str):
    sender_email = os.getenv("EMAIL")  # Replace with your email
    sender_password = os.getenv("PASSWORD")  # Use an App Password for security
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # TLS Port

    try:
        # Create an SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, sender_password)  # Login to the email account

        # Create the email content
        subject = "🔑 Password Reset Request"
        message_body = f"""
        Hello {user},

        Your password has been reset successfully. Here are the details:

        📌 **New Password**: {password}

        Please change your password immediately after logging in for security reasons.

        If you didn't request this change, please contact support immediately.

        Regards,  
        Support Team  
        """

        # Format email message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email
        msg["Subject"] = subject
        msg.attach(MIMEText(message_body, "plain"))

        # Send the email
        server.sendmail(sender_email, email, msg.as_string())

        # Close SMTP session
        server.quit()

        print("Password reset email sent successfully!")
        return True

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def generate_temp_password(length=12) -> str:

    # Ensure at least one character from each category
    upper = random.choice(string.ascii_uppercase)
    lower = random.choice(string.ascii_lowercase)
    digit = random.choice(string.digits)
    special = random.choice("!@#$%^&*")

    # Fill the rest of the password length with random choices
    remaining_length = length - 4
    all_characters = string.ascii_letters + string.digits + "!@#$%^&*"
    remaining_chars = "".join(random.choices(all_characters, k=remaining_length))

    # Shuffle to avoid predictable patterns
    password = list(upper + lower + digit + special + remaining_chars)
    random.shuffle(password)

    return "".join(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
    return encoded_jwt


def is_valid_email(email: str) -> bool:
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(email_regex, email))


def get_password_strength(password: str) -> tuple[str, bool]:
    length = len(password)
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[!@#$%^&*(),.?\":{}|<>]", password))

    if length < 6:
        return "Weak", False
    elif length < 8 and (has_upper or has_lower) and has_digit:
        return "Moderate", False
    elif length >= 8 and has_upper and has_lower and has_digit and has_special:
        return "Very Strong", True
    elif length >= 8 and has_upper and has_lower and has_digit:
        return "Strong", True  # Always return a boolean here

    return "Weak", False


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())


def get_current_user(token: str = Depends(oauth2_scheme), db=Depends(get_db)):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    cur, conn = db
    cur.execute("SELECT * FROM Users WHERE username = %s", (username,))
    user = cur.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    
    return {"username": user[1], "email": user[2]}  # Adjust indexes based on your DB structure

def random_username():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def generate_unique_referral_code(cur, conn):
    """Generates a unique referral code and ensures it doesn't exist in the database"""

    while True:
        referral_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))

        # Check if referral code already exists
        cur.execute("SELECT 1 FROM Users WHERE referral_code = %s", (referral_code,))
        if not cur.fetchone():
            return referral_code