from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
from app.pymysql.databaseConnection import get_db_connection
from app.dependencies import get_current_user
from app.models.User import User

router = APIRouter()


class Publisher(BaseModel):
    name: str


# get publishers
@router.get("/publisher/")
def get_publishers():
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM publisher")
        rows = cursor.fetchall()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success" : False, "message" : "An error occurred"}
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "rows": rows}
    )

# add a new publisher to the database
@router.post("/publisher/", response_model=User)
async def post_publisher(publisher_data: Publisher, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = publisher_data.name

        # create a cursor object
        cursor = connection.cursor()
        add_publisher_query = "INSERT INTO publisher (name) VALUES (%s)"
        cursor.execute(add_publisher_query, (name))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success" : False, "message" : "Failed to add publisher"}
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Publisher added successfully"}
    )

# edit a video game publisher
@router.put("/publisher/{publisher_id}", response_model=User)
async def put_publisher(publisher_id: int, publisher_data: Publisher, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = publisher_data.name

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM publisher WHERE publisher_id = %s", publisher_id)
        publisher = cursor.fetchone()
        if not publisher:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found"
        )
        update_publisher_query = "UPDATE publisher SET name = %s WHERE publisher_id = %s"
        cursor.execute(update_publisher_query, (name, publisher_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update publisher"
        )
    finally:
        connection.close()
    
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Publisher updated successfully"}
    )


# delete a video game publisher
@router.delete("/publisher/{publisher_id}", response_model=User)
async def delete_publisher(publisher_id:int, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        # check if the entry exists first
        cursor.execute("SELECT * FROM publisher WHERE publisher_id = %s", publisher_id)
        publisher = cursor.fetchone()
        if not publisher:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found"
        )
        delete_publisher_query = "DELETE FROM publisher WHERE publisher_id = %s"
        cursor.execute(delete_publisher_query, (publisher_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete publisher"
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Publisher successfully deleted"}
    )