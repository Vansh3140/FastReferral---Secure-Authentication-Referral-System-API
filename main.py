from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
import os
from utility import (
        get_db,
        generate_temp_password, 
        create_access_token, 
        is_valid_email,
        get_password_strength, 
        hash_password, 
        verify_password,
        get_current_user,
        send_password,
        generate_unique_referral_code
)
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from models import Register, ResetPasswordRequest, ForgotPasswordRequest, UserResponse
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register")
async def register_user(user_info: Register, db=Depends(get_db)):
    cur, conn = db

    # Check if email already exists
    cur.execute("SELECT * FROM Users WHERE email = %s", (user_info.email,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Check if username is already taken
    cur.execute("SELECT * FROM Users WHERE username = %s", (user_info.username,))
    if cur.fetchone():
        raise HTTPException(status_code=400, detail="Username already taken.")

    referred_by = None
    referrer_id = None
    if user_info.referral_code:
        cur.execute("SELECT id, referral_code FROM Users WHERE referral_code = %s", (user_info.referral_code,))
        referrer = cur.fetchone()
        if not referrer:
            raise HTTPException(status_code=400, detail="Invalid Referral Code.")
        referrer_id = referrer[0]  # Get referrer user ID
        referred_by = referrer[1]  # Get the actual referral code

    # Validate password strength
    password_strength, is_good = get_password_strength(user_info.password)
    if not is_good:
        return {"message": f"{password_strength} Password Entered!"}

    # Validate email format
    if not is_valid_email(user_info.email):
        return {"message": "Enter a valid Email"}

    # Hash password
    hashed_password = hash_password(user_info.password)

    # Generate a unique referral code for the new user
    generated_code = generate_unique_referral_code(cur=cur, conn=conn)

    # Insert new user into Users table
    cur.execute(
        """INSERT INTO Users (username, password_hash, email, referred_by, referral_code) 
           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
        (user_info.username, hashed_password, user_info.email, referred_by, generated_code),
    )
    new_user_id = cur.fetchone()[0]  # Fetch new user ID

    # If referrer_id exists, insert a record into Referrals table
    if referrer_id:
        cur.execute(
            """INSERT INTO Referrals (referrer_id, referred_user_id, status) 
               VALUES (%s, %s, %s)""",
            (referrer_id, new_user_id, "successful"),
        )

        # Reward the referrer (example: giving 10.00 credits)
        cur.execute(
            """INSERT INTO Rewards (user_id, reward_type, reward_amount, reward_status) 
               VALUES (%s, %s, %s, %s)""",
            (referrer_id, "Referral Bonus", 10.00, "pending"),
        )

    conn.commit()

    return {
        "message": "User registered successfully!",
        "referral_code": generated_code,
    }


@app.post("/api/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db=Depends(get_db)):
    cur, conn = db
    cur.execute("SELECT * FROM Users WHERE username = %s", (form_data.username,))
    user = cur.fetchone()
    
    if not user or not verify_password(form_data.password, user[3]):  # Adjust index for password hash
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user[1]}, expires_delta=timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))))
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/forgot-password")
async def forget_password_user(user_info: ForgotPasswordRequest, db=Depends(get_db)):
    cur, conn = db
    cur.execute("SELECT * FROM Users WHERE username = %s", (user_info.username,))
    user = cur.fetchone()

    if not user:
        raise HTTPException(status_code=400, detail="User not found.")

    if user_info.email != user[2]:
        raise HTTPException(status_code=400, detail="Email does not match our records.")
    
    
    temp_password = generate_temp_password()
    hashed_password = hash_password(temp_password)

    # Update password in the database
    cur.execute("UPDATE Users SET password_hash = %s WHERE username = %s", (hashed_password, user_info.username))
    conn.commit()

    is_success = send_password(password=temp_password, email=user_info.email, user=user_info.username)

    if is_success:
        return {"message": f"Password sent to {user_info.email} successfully."}
    else:
        raise HTTPException(status_code=500, detail="Error while changing password. Please Try Again!")


@app.post("/api/reset-password")
async def reset_password_user(user_info: ResetPasswordRequest, db=Depends(get_db)):
    cur, conn = db
    cur.execute("SELECT * FROM Users WHERE username = %s", (user_info.old_username,))
    user = cur.fetchone()
    
    if not user or not verify_password(user_info.old_password, user[3]):  # Adjust index for password hash
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    password_strength, is_good = get_password_strength(user_info.new_password)
    if not is_good:
        return {"message": f"{password_strength} Password Entered!"}

    hashed_password = hash_password(user_info.new_password)

    # Update password in the database
    cur.execute("UPDATE Users SET password_hash = %s WHERE username = %s", (hashed_password, user_info.username))
    conn.commit()

    return {"message": "Password Updated Successfully."}
    

@app.get("/api/referrals")
async def referrals_by_user(current_user: UserResponse = Depends(get_current_user), db=Depends(get_db)):
    """Retrieve all users referred by the logged-in user"""
    cur, conn = db

    cur.execute("""
        SELECT u.username, u.email, r.date_referred, r.status
        FROM Users u
        JOIN Referrals r ON u.id = r.referred_user_id
        WHERE r.referrer_id = (SELECT id FROM Users WHERE username = %s);
    """, (current_user["username"],))

    referrals = cur.fetchall()
    
    if not referrals:
        return {"message": "No referrals found"}

    result = [{"username": row[0], "email": row[1], "date_referred": row[2], "status": row[3]} for row in referrals]
    
    return {"referrals": result}


@app.get("/api/referral-stats")
async def referral_stats_user(current_user: UserResponse = Depends(get_current_user), db=Depends(get_db)):
    """Retrieve referral statistics for the logged-in user"""
    cur, conn = db

    cur.execute("""
        SELECT COUNT(*) FROM Referrals 
        WHERE referrer_id = (SELECT id FROM Users WHERE username = %s) 
        AND status = 'successful';
    """, (current_user["username"],))
    successful_referrals = cur.fetchone()[0]

    cur.execute("""
        SELECT SUM(reward_amount) FROM Rewards 
        WHERE user_id = (SELECT id FROM Users WHERE username = %s) 
        AND reward_status = 'claimed';
    """, (current_user["username"],))
    total_rewards = cur.fetchone()[0] or 0

    return {
        "successful_referrals": successful_referrals,
        "total_rewards": total_rewards
    }
