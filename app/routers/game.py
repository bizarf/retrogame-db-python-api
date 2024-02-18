from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
from app.pymysql.databaseConnection import get_db_connection
from app.dependencies import get_current_user
from app.models.User import User

router = APIRouter()


class Game(BaseModel):
    title: str
    description: str
    release_year: int
    genre_id: int
    platform_id: int
    publisher_id: int
    developer_id: int
    image_url: str = None


# get games
@router.get("/games/")
def get_games():
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM game")
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


# fetch details about a single game
@router.get("/game/{game_id}")
def get_game(game_id):
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        select_single_game_query = "SELECT * FROM game WHERE game_id = %s"
        cursor.execute(select_single_game_query, (game_id,))
        game = cursor.fetchone()
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
        detail={ "success" : True, "game": game}
    )


# add a new game to the database
@router.post("/game/", response_model=User)
async def post_game(game_data: Game, current_user: Annotated[User, Depends(get_current_user)]):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        title = game_data.title
        description = game_data.description
        release_year = game_data.release_year
        genre_id = game_data.genre_id
        platform_id = game_data.platform_id
        publisher_id = game_data.publisher_id
        developer_id = game_data.developer_id
        image_url = game_data.image_url

        values = (title, description, release_year, genre_id, platform_id, publisher_id, developer_id, image_url)

        # create a cursor object
        cursor = connection.cursor()
        add_game_query = "INSERT INTO game (title, description, release_year, platform_id, publisher_id, developer_id, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(add_game_query, (values,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success" : False, "message" : "Failed to add game"}
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Game added successfully"}
    )


# edit a video game game
@router.put("/game/{game_id}", response_model=User)
async def put_game(game_id: int, game_data: Game, current_user: Annotated[User, Depends(get_current_user)]):
    print(current_user)
    if current_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"}
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        title = game_data.title
        description = game_data.description
        release_year = game_data.release_year
        genre_id = game_data.genre_id
        platform_id = game_data.platform_id
        publisher_id = game_data.publisher_id
        developer_id = game_data.developer_id
        image_url = game_data.image_url

        values = (title, description, release_year, genre_id, platform_id, publisher_id, developer_id, image_url, game_id)

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM game WHERE game_id = %s", (game_id,))
        game = cursor.fetchone()
        if not game:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Game not found"
        )
        update_game_query = "UPDATE game SET title = %s, description = %s, release_year = %s, genre_id = %s, platform_id = %s, publisher_id = %s, developer_id = %s, image_url = %s, WHERE game_id = %s"
        cursor.execute(update_game_query, (values,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update game"
        )
    finally:
        connection.close()
    
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Game updated successfully"}
    )


# delete a video game game
@router.delete("/game/{game_id}", response_model=User)
async def delete_game(game_id:int, current_user: Annotated[User, Depends(get_current_user)]):
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
        cursor.execute("SELECT * FROM game WHERE game_id = %s", (game_id,))
        game = cursor.fetchone()
        if not game:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="game not found"
        )
        delete_game_query = "DELETE FROM game WHERE game_id = %s"
        cursor.execute(delete_game_query, (game_id,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete game"
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Game successfully deleted"}
    )