from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from typing import Annotated
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
        get_faves_query = "SELECT "
        cursor.execute(get_faves_query)
        rows = cursor.fetchone()
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