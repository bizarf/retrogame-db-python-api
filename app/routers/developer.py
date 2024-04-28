from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from app.pymysql.databaseConnection import get_db_connection
from typing import Annotated
from app.dependencies import get_current_user
from app.models.User import User
from app.utils.db_utils import get_info_list

router = APIRouter()


class Developer(BaseModel):
    name: str


# aiven is case sensitive? tables must be lowercase


# get all developers
@router.get("/developers/")
def get_developers():
    query = "SELECT developer_id, name FROM developer"
    get_info_list(query)


# fetch all data about a single developer
@router.get("/developer-data/{developer_id}")
def get_developer_data(developer_id):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        fetch_platform_data = "SELECT * FROM developer WHERE developer_id = %s"
        cursor.execute(fetch_platform_data, (developer_id,))
        developer = cursor.fetchone()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "An error occurred"},
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK, detail={"success": True, "developer": developer}
    )


# get all games developed by the developer
@router.get("/developer/{developer_id}")
def get_developer_games(developer_id):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        fetch_developer_info_query = """
            SELECT name FROM developer WHERE developer_id = %s;
            """
        cursor.execute(fetch_developer_info_query, (developer_id,))
        developer_name = cursor.fetchone()["name"]

        fetch_games_by_developer = """
            SELECT g.game_id, g.title AS game_title, g.image_url, g.genre_id, gen.name AS genre_name, g.platform_id, p.name AS platform_name, g.publisher_id, pub.name AS publisher_name
            FROM game g
            JOIN genre gen ON g.genre_id = gen.genre_id
            JOIN platform p ON g.platform_id = p.platform_id
            JOIN publisher pub ON g.publisher_id = pub.publisher_id
            WHERE g.developer_id = %s;
            """
        cursor.execute(fetch_games_by_developer, (developer_id,))
        games = cursor.fetchall()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "An error occurred"},
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "games": games, "developer_name": developer_name},
    )


# add a new developer to the database
@router.post("/developer/", response_model=User)
def post_developer(
    developer_data: Developer, current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"},
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = developer_data.name

        # create a cursor object
        cursor = connection.cursor()
        add_developer_query = "INSERT INTO developer (name) VALUES (%s)"
        cursor.execute(add_developer_query, (name,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "Failed to add developer"},
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Developer added successfully"},
    )


# edit a video game developer
@router.put("/developer/{developer_id}", response_model=User)
def put_developer(
    developer_id: int,
    developer_data: Developer,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"},
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = developer_data.name

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute(
            "SELECT * FROM developer WHERE developer_id = %s", (developer_id,)
        )
        developer = cursor.fetchone()
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
            )
        update_developer_query = (
            "UPDATE developer SET name = %s WHERE developer_id = %s"
        )
        cursor.execute(update_developer_query, (name, developer_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update developer",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Developer updated successfully"},
    )


# delete a video game developer
@router.delete("/developer/{developer_id}", response_model=User)
def delete_developer(
    developer_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"},
        )
    try:
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        # check if the entry exists first
        cursor.execute(
            "SELECT * FROM developer WHERE developer_id = %s", (developer_id,)
        )
        developer = cursor.fetchone()
        if not developer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Developer not found"
            )
        delete_developer_query = "DELETE FROM developer WHERE developer_id = %s"
        cursor.execute(delete_developer_query, (developer_id,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete developer",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Developer successfully deleted"},
    )
