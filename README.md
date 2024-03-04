# RetroGame-DB - FastAPI - Python API

This is a project where I'm making an API for a retro video game themed database using FastAPI with PyMySQL. The goal is to test and showcase the Python and MySQL knowledge that I have gained.

-   [View the live client site here](https://bizarf.github.io/retrogame-db-client/)
-   [View the RetroGame DB client repo](https://github.com/bizarf/retrogame-db-client)

<hr>

#### Install:

To run this project on your locally, first clone the repo and enter the folder in your terminal. Now setup a VENV with the command:

```
python -m venv venv
```

After that has been created activate the virtual environment by typing in your terminal:

```
venv\Scripts\activate
```

Now to install the project dependencies type:

```
pip install -r requirements.txt
```

Now create a file called ".env" at the root of the project and inside the file add:

```
MYSQL_HOST="(your MySQL hostname)"
MYSQL_USER="(your MySQL username)"
MYSQL_PASSWORD="(your MySQL password)"
MYSQL_DATABASE="(the MySQL database that you want to use)"
JWT_SECRET_KEY="(generate with command: openssl rand -hex 32)"
JWT_REFRESH_SECRET_KEY="(generate with command: openssl rand -hex 32)"
CORS_ORIGIN="(the frontend host)"
```

When everything has been done, we can start the server with:

```
uvicorn app.main:app --reload
```

<hr>
#### Features

-   [x] JWT authentication system with locked routes
-   [x] JWT access token updating via a JWT refresh token function
-   [x] MySQL integration with PyMySQL
-   [x] CRUD operations for admin level users
-   [x] Routes for handling users data
-   [x] Routes for handling platform data
-   [x] Routes for handling genre data
-   [x] Routes for handling developer data
-   [x] Routes for handling publisher data
-   [x] Routes for handling game data
-   [x] Routes for handling favourites data
-   [x] Routes for generating new access tokens
-   [] Routes for rating games system

<hr>

##### Tools and technologies used:

-   Python
-   FastAPI
-   PyMySQL
