import pymysql.cursors
from dotenv import load_dotenv
import os


load_dotenv()


# connect to the database
def get_db_connection():
    connection = pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
        )
    return connection