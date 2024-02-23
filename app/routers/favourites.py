from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
from datetime import datetime
from app.pymysql.databaseConnection import get_db_connection
from app.dependencies import get_current_user
from app.models.User import User


router = APIRouter()


class Favourites(BaseModel):
    game_id: int


# get all of the user's favourites
@router.get("/favourites/", response_model=User)
async def get_games(current_user: Annotated[User, Depends(get_current_user)]):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        get_faves_query = """
        SELECT f.favourite_id, g.game_id, g.title AS game_title, g.release_year, g.image_url, gen.genre_id, gen.name AS genre_name, plat.platform_id, plat.name AS platform_name, pub.publisher_id, pub.name AS publisher_name, d.developer_id, d.name AS developer_name
        FROM favourites f
        JOIN game g ON f.game_id = g.game_id
        JOIN genre gen ON g.genre_id = gen.genre_id
        JOIN platform plat ON plat.platform_id = g.platform_id
        JOIN publisher pub ON pub.publisher_id = g.publisher_id
        JOIN developer d ON d.developer_id = g.developer_id
        WHERE f.user_id = %s;
        """
        cursor.execute(get_faves_query, (current_user["user_id"],))
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
        status_code=status.HTTP_200_OK, detail={"success": True, "games": games}
    )


# check if the fave exists
@router.get("/favourites/{game_id}", response_model=User)
async def get_fave_check(
    game_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        get_fave_query = """
        SELECT favourite_id FROM favourites
        WHERE user_id = %s AND game_id = %s;
        """

        values = (current_user["user_id"], game_id)

        cursor.execute(get_fave_query, values)
        fave = cursor.fetchall()
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
        status_code=status.HTTP_200_OK, detail={"success": True, "fave": fave}
    )


# add a favourite to the user's list
@router.post("/favourites/", response_model=User)
async def post_favourites(
    favourites_data: Favourites,
    current_user: Annotated[User, Depends(get_current_user)],
):
    try:
        connection = get_db_connection()
        # gather values from the json object
        user_id = current_user["user_id"]
        game_id = favourites_data.game_id
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # tuple containing the values needed for the query
        values = (user_id, game_id, timestamp)

        # create a cursor object
        cursor = connection.cursor()
        check_favourite_query = (
            "SELECT * FROM favourites WHERE game_id = %s AND user_id = %s"
        )
        cursor.execute(check_favourite_query, (game_id, user_id))
        existingFave = cursor.fetchone()
        if existingFave:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Favourite entry already exists",
            )

        add_favourite_query = (
            "INSERT INTO favourites (user_id, game_id, timestamp) VALUES (%s, %s, %s)"
        )

        cursor.execute(add_favourite_query, values)
        connection.commit()
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "Failed to add favourite"},
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Favourite added successfully"},
    )


# delete a favourite
@router.delete("/favourites/{favourite_id}", response_model=User)
async def delete_genre(
    favourite_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        # check if the entry exists first
        cursor.execute(
            "SELECT * FROM favourites WHERE favourite_id = %s", (favourite_id,)
        )
        favourite = cursor.fetchone()

        if not favourite:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Favourite not found"
            )
        # if the favourite does not belong to the current user, then raise a 401
        if favourite["user_id"] != current_user["user_id"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": "You are unauthorized to delete this favourite"},
            )
        delete_genre_query = "DELETE FROM favourites WHERE favourite_id = %s"
        cursor.execute(delete_genre_query, (favourite_id,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete favourite",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Favourite successfully deleted"},
    )
