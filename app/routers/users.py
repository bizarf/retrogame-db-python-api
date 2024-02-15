from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Annotated
from datetime import datetime
from app.pymysql.databaseConnection import get_db_connection
from app.utils import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    create_refresh_token)
from app.dependencies import get_current_user
from app.models.User import User


router = APIRouter()


# i only need the username, email, and password for registering users. role can be set via mysql. date is automatically generated
class UserRegistration(BaseModel):
    username: str
    # make sure user enters an email formatted string
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


# user registration
@router.post("/users/register")
def post_user_register(user_registration: UserRegistration):
    try:
        connection = get_db_connection()
        # gather values from the json object
        username = user_registration.username
        email = user_registration.email
        # hash the password here
        hashed_password = get_password_hash(user_registration.password)
        # generate the datetime, and format it to the mysql requirement
        join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # create a cursor object
        cursor = connection.cursor()
        add_user_query = "INSERT INTO users (username, email, password, join_date) VALUES (%s, %s, %s, %s)"
        cursor.execute(add_user_query, (username, email, hashed_password, join_date))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"success" : False, "message" : "Failed to add user"}
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "User added successfully"}
    )


# user login
@router.post("/users/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    try:
        email = form_data.username
        password = form_data.password

        # Check if user exists and verify password
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", email)
        user = cursor.fetchone()
        if not user or not verify_password(password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )
    except Exception as e:
        print(e)
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect email or password"
            )
    finally:
        connection.close()

    # Generate access and refresh tokens
    access_token = create_access_token(
        data={"sub": user["email"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["email"]}
    )

    # Return access token
    return {"success":True, "access_token": access_token, "refresh_token": refresh_token}


# fetch user details
# @router.get("/users/{user_id}")
# def get_user(user_id: int):
#     try:
#         connection = get_db_connection()

#         # create a cursor object
#         cursor = connection.cursor()
#         # check if the entry exists first
#         cursor.execute("SELECT username, email, join_date FROM users WHERE user_id = %s", user_id)
#         user = cursor.fetchone() 
#     except Exception as e:
#         print(e)
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User not found"
#         )
#     finally:
#         connection.close()
#     # make a user_data dictionary as we need to convert join_date back to the right format
#     user_data = {
#         "username": user["username"],
#         "email": user["email"],
#         "join_date": user["join_date"].strftime("%Y-%m-%d %H:%M:%S")
#     }
#     # on successful operation, send status 200 and messages
#     raise HTTPException(
#         status_code=status.HTTP_200_OK,
#         detail={ "success" : True, "user": user_data }
#     )


# user update
# @router.put("/user/{user_id}")
# def put_user_update():
#     return {"hello":"hello"}


# returns the current user
@router.get("/users/me/", response_model=User)
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user