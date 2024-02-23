import pymysql.cursors
from dotenv import load_dotenv
import os


load_dotenv()


# connect to the database
def get_db_connection():
    # localhost mysql connection testing
    # connection = pymysql.connect(
    #     host=os.getenv("MYSQL_HOST"),
    #     user=os.getenv("MYSQL_USER"),
    #     password=os.getenv("MYSQL_PASSWORD"),
    #     database=os.getenv("MYSQL_DATABASE"),
    #     cursorclass=pymysql.cursors.DictCursor,
    # )

    # aiven connection
    timeout = 10
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8mb4",
        connect_timeout=timeout,
        read_timeout=timeout,
        port=27369,
        write_timeout=timeout,
    )
    return connection
