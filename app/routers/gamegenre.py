from fastapi import APIRouter, HTTPException, status
from app.pymysql.databaseConnection import get_db_connection

router = APIRouter()


# get publishers
@router.get("/gamegenre/{game_id}/")
def get_gameGenre(game_id: int):
    try:        
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        get_gameGenre_query = """
            SELECT g.name AS genre_name
            FROM GENRE g
            JOIN GAMEGENRE gg ON g.genre_id = gg.genre_id
            WHERE gg.game_id = %s;
            """
        cursor.execute(get_gameGenre_query, game_id)
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