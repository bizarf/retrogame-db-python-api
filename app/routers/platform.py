from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel,HttpUrl, validator
from typing import Optional
from app.pymysql.databaseConnection import get_db_connection

router = APIRouter()


class Platform(BaseModel):
    name: str
    logo_url: Optional[HttpUrl] = None

    # custom validator to allow an empty string
    @validator('logo_url', pre=True, always=True)
    def empty_string_to_none(cls, v):
        if v == "":
            return None
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
            detail={"success" : False, "message" : "An error occurred"}
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "rows": rows}
    )

# add a new platform to the database
@router.post("/platform/")
def post_platform(platform_data: Platform):
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
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success" : False, "message" : "Failed to add platform"}
        )
    finally:
        connection.close()
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Platform added successfully"}
    )

# edit a video game platform
@router.put("/platform/{platform_id}")
def put_platform(platform_id: int, platform_data: Platform):
    try:
        connection = get_db_connection()
        # gather values from the json object
        name = platform_data.name
        logo_url = platform_data.logo_url

        # create a cursor object
        cursor = connection.cursor()
        # check if the entry exists first
        cursor.execute("SELECT * FROM platform WHERE platform_id = %s", platform_id)
        platform = cursor.fetchone()
        if not platform:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
        update_platform_query = "UPDATE platform SET name = %s, logo_url = %s WHERE platform_id = %s"
        cursor.execute(update_platform_query, (name, logo_url, platform_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update platform"
        )
    finally:
        connection.close()
    
    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Platform updated successfully"}
    )


# delete a video game platform
@router.delete("/platform/{platform_id}")
def delete_platform(platform_id:int):
    try:
        connection = get_db_connection()
        # create a cursor object
        cursor = connection.cursor()

        # check if the entry exists first
        cursor.execute("SELECT * FROM platform WHERE platform_id = %s", platform_id)
        platform = cursor.fetchone()
        if not platform:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform not found"
        )
        delete_platform_query = "DELETE FROM platform WHERE platform_id = %s"
        cursor.execute(delete_platform_query, (platform_id))
        connection.commit()
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete platform"
        )
    finally:
        connection.close()

    # on successful operation, send status 200 and messages
    raise HTTPException(
        status_code=status.HTTP_200_OK,
        detail={ "success" : True, "message": "Platform successfully deleted"}
    )