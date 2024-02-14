from fastapi import FastAPI
from app.routers import (
    users, 
    platform,
    genre,
    developer,
    publisher,
    game,
    favourites
    )

app = FastAPI()


@app.get("/")
def root():
    return {"message":"Welcome to the RetroGame API"}


app.include_router(users.router)
app.include_router(platform.router)
app.include_router(genre.router)
app.include_router(developer.router)
app.include_router(publisher.router)
app.include_router(game.router)
app.include_router(favourites.router)