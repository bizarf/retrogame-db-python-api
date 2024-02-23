import os
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, HttpUrl, validator, ValidationError
from typing import Optional, Annotated
from app.pymysql.databaseConnection import get_db_connection
from app.dependencies import get_current_user
from app.models.User import User
import re

router = APIRouter()


class Platform(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None

    # custom validator to allow an empty string
    @validator("logo_url", pre=True, always=True)
    def validate_logo_url(cls, v):
        if v is None or v == "":
            return None
        elif not re.match(r".+\.(jpg|jpeg|png|gif|bmp|svg)$", v):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"success": False, "message": "The URL must point to an image"},
            )
        return v


# get all platforms
@router.get("/platforms/")
def get_platforms():
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM platform")
        rows = cursor.fetchall()
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
        status_code=status.HTTP_200_OK, detail={"success": True, "rows": rows}
    )


# fetch all data about single platform
@router.get("/platform-data/{platform_id}")
def get_platform_data(platform_id):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        fetch_platform_data = "SELECT * FROM platform WHERE platform_id = %s"
        cursor.execute(fetch_platform_data, (platform_id,))
        platform = cursor.fetchone()
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
        status_code=status.HTTP_200_OK, detail={"success": True, "platform": platform}
    )


# get all games for a platform
@router.get("/platform/{platform_id}")
def get_platform_games(platform_id: int):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        fetch_platform_info_query = """
            SELECT name FROM PLATFORM WHERE platform_id = %s;
            """
        cursor.execute(fetch_platform_info_query, (platform_id,))
        platform_name = cursor.fetchone()["name"]

        fetch_games_for_platform_query = """
            SELECT g.game_id, g.title AS game_title, g.image_url, gen.name AS genre_name, g.genre_id, g.developer_id, d.name AS developer_name, g.publisher_id, pub.name AS publisher_name
            FROM GAME g
            JOIN GENRE gen ON g.genre_id = gen.genre_id
            JOIN DEVELOPER d ON d.developer_id = g.developer_id
            JOIN PUBLISHER pub ON pub.publisher_id = g.publisher_id
            WHERE g.platform_id = %s;
            """

        cursor.execute(fetch_games_for_platform_query, (platform_id,))
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
        detail={"success": True, "games": games, "platform_name": platform_name},
    )


# add a new platform to the database
@router.post("/platform/", response_model=User)
async def post_platform(
    platform_data: Platform, current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"},
        )
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = platform_data.name
        logo_url = platform_data.logo_url

        # create a cursor object
        cursor = connection.cursor()
        add_platform_query = "INSERT INTO platform (name, logo_url) VALUES (%s, %s)"
        cursor.execute(add_platform_query, (name, logo_url))
        connection.commit()
    except HTTPException as http_exception:
        raise http_exception
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "message": "Failed to add platform"},
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Platform added successfully"},
    )


# edit a video game platform
@router.put("/platform/{platform_id}", response_model=User)
async def put_platform(
    platform_id: int,
    platform_data: Platform,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if current_user["role"] == "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "message": "You are unauthorized"},
        )

    try:
        connection = get_db_connection()
        # gather values from the json object and make a tuple for the sql query
        name = platform_data.name
        logo_url = platform_data.logo_url

        values = (name, logo_url, platform_id)

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM platform WHERE platform_id = %s", (platform_id,))
        platform = cursor.fetchone()
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found"
            )
        update_platform_query = (
            "UPDATE platform SET name = %s, logo_url = %s WHERE platform_id = %s"
        )
        cursor.execute(update_platform_query, values)
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update platform",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Platform updated successfully"},
    )


# delete a video game platform
@router.delete("/platform/{platform_id}", response_model=User)
async def delete_platform(
    platform_id: int, current_user: Annotated[User, Depends(get_current_user)]
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
        cursor.execute("SELECT * FROM platform WHERE platform_id = %s", (platform_id,))
        platform = cursor.fetchone()
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Platform not found"
            )
        delete_platform_query = "DELETE FROM platform WHERE platform_id = %s"
        cursor.execute(delete_platform_query, (platform_id,))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete platform",
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={"success": True, "message": "Platform successfully deleted"},
    )
