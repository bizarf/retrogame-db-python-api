from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime
from app.pymysql.databaseConnection import get_db_connection
from app.dependencies import get_current_user
from app.models.User import User


router = APIRouter()


class Favourites(BaseModel):
    user_id: int
    game_id: int


# get all of the user's favourites
@router.get("/favourites/", response_model=User)
def get_games(current_user: Annotated[User, Depends(get_current_user)]):
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        get_faves_query = """
        SELECT g.game_id, g.title AS game_title, g.description AS game_description, g.release_year AS game_release_year, g.image_url AS game_image_url
        FROM FAVOURITES f
        JOIN GAME g ON f.game_id = g.game_id
        WHERE f.user_id = %s;
        """
        cursor.execute(get_faves_query, current_user["user_id"])
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


# add a favourite to the user's list
@router.post("/favourites/", response_model=User)
async def post_favourites(favourites_data: Favourites, current_user: Annotated[User, Depends(get_current_user)]):
    try:
        connection = get_db_connection()
        # gather values from the json object
        user_id = current_user["user_id"]
        game_id = favourites_data.game_id
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # tuple containing the values needed for the query
        values = (user_id, game_id, timestamp)

        # create a cursor object
        cursor = connection.cursor()
        add_favourite_query = "INSERT INTO FAVOURITES (user_id, game_id, timestamp) VALUES (%s, %s, %s)"
        cursor.execute(add_favourite_query, values)
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success" : False, "message" : "Failed to add favourite"}
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Favourite added successfully"}
    )


# delete a favourite
@router.delete("/favourites/{favourite_id}", response_model=User)
async def delete_genre(favourite_id:int, current_user: Annotated[User, Depends(get_current_user)]):
    try:
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        # check if the entry exists first
        cursor.execute("SELECT * FROM favourites WHERE favourite_id = %s", favourite_id)
        favourite = cursor.fetchone()
        if not favourite:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favourite not found"
        )
        # if the favourite does not belong to the current user, then raise a 401
        if favourite[0] != current_user["user_id"]:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"message": "You are unauthorized to delete this favourite"}
        )
        delete_genre_query = "DELETE FROM favourites WHERE favourite_id = %s"
        cursor.execute(delete_genre_query, favourite_id)
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete favourite"
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Favourite successfully deleted"}
    )