from fastapi import FastAPI
from app.routers import users, platform

app = FastAPI()


@app.get("/")
def root():
    return {"message":"Welcome to the RetroGame API"}


app.include_router(users.router)
app.include_router(platform.router)