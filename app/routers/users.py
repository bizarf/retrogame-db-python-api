from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from datetime import datetime
from app.pymysql.databaseConnection import get_db_connection

router = APIRouter()


class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str
    join_date: datetime


# user registration
@router.post("/users/register")
def post_user_register():
    return {"hello": "hello"}


# user login
@router.post("/users/login")
def post_user_login():
    return {"hello": "hello"}


# fetch user details
@router.get("/users/<user_id>")
def get_user(user_id: int):
    try:
        connection = get_db_connection()

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM users WHERE user_id = %s", user_id)
        user = cursor.fetchone() 
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    finally:
        connection.close()
    
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "user": user }
    )


# user update
@router.put("/user/<user_id>")
def put_user_update():
    return {"hello":"hello"}