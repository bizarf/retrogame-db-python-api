from fastapi import HTTPException, status
from app.pymysql.databaseConnection import get_db_connection


def get_info_list(category_query):
    try:
        # make a database connection
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()
        cursor.execute(category_query)
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
