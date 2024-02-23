from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    users,
    platform,
    genre,
    developer,
    publisher,
    game,
    favourites,
    token,
)


app = FastAPI()
# cors stuff. must change allow_origin to github later
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://bizarf.github.io/retrogame-db-client"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def root():
    return {"message": "Welcome to the RetroGame API"}


app.include_router(users.router)
app.include_router(platform.router)
app.include_router(genre.router)
app.include_router(developer.router)
app.include_router(publisher.router)
app.include_router(game.router)
app.include_router(favourites.router)
app.include_router(token.router)
