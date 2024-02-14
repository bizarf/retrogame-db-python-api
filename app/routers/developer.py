from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.pymysql.databaseConnection import get_db_connection
from typing import Annotated
from app.dependencies import get_current_user
from app.models.User import User

router = APIRouter()


class Developer(BaseModel):
    name: str


# get all developers
@router.get("/developers/")
def get_developers():
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM developer")
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


# get all games developed by the developer
@router.get("/developer/{developer_id}")
def get_developer_games(developer_id):
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        fetch_games_by_developer = """
            SELECT g.game_id, g.title AS game_title, g.image_url, d.name AS developer_name
            FROM GAME g
            JOIN DEVELOPER d ON g.developer_id = d.developer_id
            WHERE g.developer_id = %s;
            """
        cursor.execute(fetch_games_by_developer, developer_id)
        games = cursor.fetchall()
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
        detail={ "success" : True, "games": games}
    )


# add a new developer to the database
@router.post("/developer/", response_model=User)
def post_developer(developer_data: Developer, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = developer_data.name

        # create a cursor object
        cursor = connection.cursor()
        add_developer_query = "INSERT INTO developer (name) VALUES (%s)"
        cursor.execute(add_developer_query, name)
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success" : False, "message" : "Failed to add developer"}
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Developer added successfully"}
    )

# edit a video game developer
@router.put("/developer/{developer_id}", response_model=User)
def put_developer(developer_id: int, developer_data: Developer, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = developer_data.name

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM developer WHERE developer_id = %s", developer_id)
        developer = cursor.fetchone()
        if not developer:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found"
        )
        update_developer_query = "UPDATE developer SET name = %s WHERE developer_id = %s"
        cursor.execute(update_developer_query, (name, developer_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update developer"
        )
    finally:
        connection.close()
    
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Developer updated successfully"}
    )


# delete a video game developer
@router.delete("/developer/{developer_id}", response_model=User)
def delete_developer(developer_id:int, current_user: Annotated[User, Depends(get_current_user)]):
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
        cursor.execute("SELECT * FROM developer WHERE developer_id = %s", developer_id)
        developer = cursor.fetchone()
        if not developer:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Developer not found"
        )
        delete_developer_query = "DELETE FROM developer WHERE developer_id = %s"
        cursor.execute(delete_developer_query, developer_id)
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete developer"
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Developer successfully deleted"}
    )