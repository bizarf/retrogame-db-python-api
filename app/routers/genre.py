from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
from app.pymysql.databaseConnection import get_db_connection
from app.dependencies import get_current_user
from app.models.User import User
from app.utils.db_utils import get_info_data, get_info_list

router = APIRouter()


class Genre(BaseModel):
    name: str


# get all genres
@router.get("/genres/")
def get_genres():
    query = "SELECT genre_id, name FROM genre"
    get_info_list(query)


# fetch all data about a single genre
@router.get("/genre-data/{genre_id}")
def get_genre_data(genre_id):
    fetch_genre_data = "SELECT genre_id, name FROM genre WHERE genre_id = %s"
    get_info_data(fetch_genre_data, "genre", genre_id)


# get all games under that genre
@router.get("/genre/{genre_id}")
def get_genre_games(genre_id):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        fetch_genre_info_query = """
            SELECT name FROM genre WHERE genre_id = %s;
            """
        cursor.execute(fetch_genre_info_query, (genre_id,))
        genre_name = cursor.fetchone()["name"]

        fetch_games_by_genre = """
            SELECT g.game_id, g.title AS game_title, g.image_url, p.name AS platform_name, g.platform_id, g.developer_id, d.name AS developer_name, g.publisher_id, pub.name AS publisher_name
            FROM game g
            JOIN platform p ON g.platform_id = p.platform_id
            JOIN developer d ON g.developer_id = d.developer_id
            JOIN publisher pub ON g.publisher_id = pub.publisher_id
            WHERE g.genre_id = %s;
            """
        cursor.execute(fetch_games_by_genre, (genre_id,))
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
        detail={"success": True, "games": games, "genre_name": genre_name},
    )


# add a new genre to the database
@router.post("/genre/", response_model=User)
async def post_genre(
    genre_data: Genre, current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"},
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = genre_data.name

        # create a cursor object
        cursor = connection.cursor()
        add_genre_query = "INSERT INTO genre (name) VALUES (%s)"
        cursor.execute(add_genre_query, (name,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "Failed to add genre"},
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Genre added successfully"},
    )


# edit a video game genre
@router.put("/genre/{genre_id}", response_model=User)
async def put_genre(
    genre_id: int,
    genre_data: Genre,
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
        name = genre_data.name

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM genre WHERE genre_id = %s", (genre_id,))
        genre = cursor.fetchone()
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found"
            )
        update_genre_query = "UPDATE genre SET name = %s WHERE genre_id = %s"
        cursor.execute(update_genre_query, (name, genre_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update genre",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Genre updated successfully"},
    )


# delete a video game genre
@router.delete("/genre/{genre_id}", response_model=User)
async def delete_genre(
    genre_id: int, current_user: Annotated[User, Depends(get_current_user)]
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
        cursor.execute("SELECT * FROM genre WHERE genre_id = %s", (genre_id,))
        genre = cursor.fetchone()
        if not genre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found"
            )
        delete_genre_query = "DELETE FROM genre WHERE genre_id = %s"
        cursor.execute(delete_genre_query, (genre_id,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete genre",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Genre successfully deleted"},
    )
