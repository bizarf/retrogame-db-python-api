from typing import Optional
from passlib.context import CryptContext
from app.pymysql.databaseConnection import get_db_connection
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# jwt stuff. secret generated with:
# openssl rand -hex 32
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_SECRET_KEY = os.getenv("JWT_REFRESH_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7


# verify the user inputted password to a hashed password
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# hash and salt a password
def get_password_hash(password):
    return pwd_context.hash(password)


# check if the user exists in the database
def get_user(email: str):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", email)
    user = cursor.fetchone()
    cursor.close()
    connection.close()
    return user


# create the access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    # to_encode.update({"exp": expire})
    to_encode["exp"] = expire
    # Set the issued at time
    to_encode["iat"] = datetime.now(timezone.utc)
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# create the refresh token
def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=REFRESH_TOKEN_EXPIRE_MINUTES
        )
    # to_encode.update({"exp": expire})
    to_encode["exp"] = expire
    # Set the issued at time
    to_encode["iat"] = datetime.now(timezone.utc)
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def update_refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(
            refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=["HS256"]
        )

        if datetime.utcnow() < datetime.utcfromtimestamp(payload["exp"]):
            to_encode = payload
            encoded_jwt = jwt.encode(
                to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM
            )
            return encoded_jwt
    except JWTError as e:
        # Handle JWT errors
        print(f"JWT Error: {e}")
        return None


def verify_refresh_token(refresh_token: str):
    try:
        # Verify the token's signature
        payload = jwt.decode(
            refresh_token, JWT_REFRESH_SECRET_KEY, algorithms=["HS256"]
        )

        # Check token expiration
        if datetime.utcnow() > datetime.utcfromtimestamp(payload["exp"]):
            # Token has expired
            return None

        # Extract user ID from token payload
        user_id = payload.get("sub")

        return user_id

    except JWTError as e:
        # Handle JWT errors
        print(f"JWT Error: {e}")
        return None
