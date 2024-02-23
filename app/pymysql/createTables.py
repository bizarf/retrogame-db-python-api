import pymysql
from databaseConnection import get_db_connection


# this script will create the necessary tables for the database
try:
    # get the connection object
    connection = get_db_connection()
    # cursor interacts with the database
    cursor = connection.cursor()

    create_platform_tbl = """
        CREATE TABLE IF NOT EXISTS platform(
            platform_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            logo_url VARCHAR(255)
        );"""

    create_publisher_tbl = """
        CREATE TABLE IF NOT EXISTS publisher(
            publisher_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        );"""

    create_developer_tbl = """
        CREATE TABLE IF NOT EXISTS developer(
            developer_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        );"""

    create_genre_tbl = """
        CREATE TABLE IF NOT EXISTS genre(
            genre_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE
        );"""

    create_game_tbl = """
        CREATE TABLE IF NOT EXISTS game(
            game_id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            release_year INT NOT NULL,
            genre_id INT NOT NULL,
            platform_id INT NOT NULL,
            publisher_id INT NOT NULL,
            developer_id INT NOT NULL,
            image_url VARCHAR(255),
            FOREIGN KEY (genre_id) REFERENCES genre(genre_id),
            FOREIGN KEY (platform_id) REFERENCES platform(platform_id),
            FOREIGN KEY (publisher_id) REFERENCES publisher(publisher_id),
            FOREIGN KEY (developer_id) REFERENCES developer(developer_id)
        );"""

    create_users_tbl = """
        CREATE TABLE IF NOT EXISTS users(
            user_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            email VARCHAR(100) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(6) CHECK (role IN ('admin', 'editor', 'user')) NOT NULL DEFAULT 'user',
            join_date DATETIME NOT NULL
        );"""

    create_ratings_tbl = """
        CREATE TABLE IF NOT EXISTS ratings(
            rating_id INT AUTO_INCREMENT PRIMARY KEY,
            game_id INT NOT NULL,
            user_id INT NOT NULL,
            score INT,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (game_id) REFERENCES game(game_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );"""

    create_favourites_tbl = """
        CREATE TABLE IF NOT EXISTS favourites(
            favourite_id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            game_id INT NOT NULL,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (game_id) REFERENCES game(game_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        );"""

    cursor.execute(create_platform_tbl)
    cursor.execute(create_publisher_tbl)
    cursor.execute(create_developer_tbl)
    cursor.execute(create_genre_tbl)
    cursor.execute(create_game_tbl)
    cursor.execute(create_users_tbl)
    cursor.execute(create_ratings_tbl)
    cursor.execute(create_favourites_tbl)
    connection.commit()
except pymysql.Error as e:
    print("An error occurred:", e)
    # undo any changes
    connection.rollback()
finally:
    # close the cursor and connection
    cursor.close()
    connection.close()
